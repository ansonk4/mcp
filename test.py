from fastmcp import Client
from google import genai
from google.genai import types
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any


# Load environment variables
load_dotenv()

system_prompt = """You are a helpful Data Analysis Assistant.  
Introduce yourself to the user as their data analysis partner. Your role is to work with Excel files located in the 'data/' directory and perform analysis tasks such as summarization, visualization, and answering questions about the data.  

Steps to follow:  
1. Start by greeting the user and briefly explaining your capabilities.  
2. List all available Excel files in the 'data/' directory.  
3. Ask the user to choose one file for analysis.  
4. After the user selects a file, ask them what type of analysis they would like to perform.  
5. When interpreting user input:  
    - The input does not need to exactly match file names or column names.  
    - You should use natural language understanding and your tools to infer what the user means, mapping their request to the closest matching file, sheet, or column.  

Special formatting rule:  
- If your response contains a link to an image, you must return a JSON object **only**, with the following format and no other text:  

{
    "text": [Your textual explanation of the analysis and visualization],
    "image_path": "/tmp/graph_12345.png"
}

Keep your responses clear, structured, and conversational.
"""


class MCPClient:
    def __init__(self):
        self.gemini_client = genai.Client()
        self.mcp_client = None
        self.tools = None
        self.messages = []

    async def connect_to_server(self, server_url: str = "http://127.0.0.1:9000/mcp"):
        """Connect to the MCP server"""
        try:
            self.mcp_client = Client(server_url)
            async with self.mcp_client:
                self.tools = await self.mcp_client.list_tools()
            return True
        except Exception as e:
            print(f"Failed to connect to MCP server: {str(e)}")
            return False


    async def call_tool(self, response):
        tool_name = response.candidates[0].content.parts[0].function_call.name
        tool_args = response.candidates[0].content.parts[0].function_call.args

        print(f"Calling tool: {tool_name} with args: {tool_args}")

        try:
            async with self.mcp_client:
                result = await self.mcp_client.call_tool(tool_name, tool_args)

            function_response_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": result},
            )

            # Append function call and result of the function execution to contents
            self.messages.append(response.candidates[0].content) # Append the content from the model's response.
            self.messages.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

        except Exception as e:
            print(f"Error calling tool {tool_name}: {e}")
            # Add error response to messages to continue the conversation
            error_part = types.Part.from_function_response(
                name=tool_name,
                response={"result": f"Error: {str(e)}"},
            )
            self.messages.append(response.candidates[0].content)
            self.messages.append(types.Content(role="user", parts=[error_part]))

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.messages,
            config=config,
        )

        return response



    async def call_gemini(self) -> str:
        def convert_tool_format(tool):
            converted_tool = {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.inputSchema["properties"],
                }
            }
            return converted_tool

        available_tools = [convert_tool_format(tool) for tool in self.tools]
        tools = types.Tool(function_declarations=available_tools)

        response = self.gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=self.messages,
            config=types.GenerateContentConfig(
                        tools=[tools],
                        system_instruction=system_prompt
                    )
        )

        for response
        while response.candidates[0].content.parts[0].function_call:
            response = await self.call_tool(response)

        return response
    
    
    async def process_query(self, query: str):
        """Process a user query and return the response"""
        if not self.mcp_client:
            raise Exception("MCP client is not connected")
            
        self.messages.append({"role": "user", "parts": [{"text": query}]})
        response = await self.call_gemini()
        self.messages.append({"role": "model", "parts": response.candidates[0].content.parts})

        return response

    async def process_query_loop(self, query: str):
        response = await self.process_query(query)
        
async def main():
    """Main function to run the MCP client"""
    client = MCPClient()
    connected = await client.connect_to_server()

    if not connected:
        return

    while True:
        try:
            user_input = input("\nYou: ")
            await client.process_query_loop(user_input)

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())



