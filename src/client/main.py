from fastmcp import Client
from google import genai
from google.genai import types
import asyncio
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import json 

# import prompt
from . import prompt
from .next_speaker_detection import ConversationController

# Load environment variables
load_dotenv()

class MCPClient:
    def __init__(self):
        self.gemini_client = genai.Client()
        self.mcp_client = None
        self.tools = None
        self.messages = []
        self.ConversationController = ConversationController(self.gemini_client)

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

    async def call_gemini(self):
        """Call Gemini API with current messages"""
        if not self.mcp_client:
            raise Exception("MCP client is not connected")
            
        async with self.mcp_client:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.messages,
                config=genai.types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[self.mcp_client.session],
                    system_instruction=prompt.system_prompt,
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True
                    )
                )
            )
        return response
    
    async def process_query(self, query: str, check_continue:bool = True):
        """Process a user query and return the response"""
        if not self.mcp_client:
            raise Exception("MCP client is not connected")
            
        self.messages.append({"role": "user", "parts": [{"text": query}]})
        response = await self.call_gemini()
        self.messages.append({"role": "model", "parts": response.candidates[0].content.parts})

        if check_continue:
            should_continue, detection_result = await self.ConversationController.process_turn(self.messages)
        else:
            should_continue, detection_result = False, None

        return response, should_continue, detection_result

    def check_json(self, response_text: str):
        try:
            json_data = json.loads(response_text)
            return json_data
        except json.JSONDecodeError:
            return None

    async def process_query_loop(self, query: str):
        should_continue = True
        while should_continue:
            response, should_continue, detection_result = await self.process_query(query)

            for part in response.candidates[0].content.parts:
                    if not part.text:
                        continue
                    if part.thought:
                        print("Thought summary:")
                        print(part.text)
                        print()
                    else:
                        print("Answer:")
                        print(part.text)
                        print()

            query = "Please continue"

            print("Should Continue:", should_continue)

    async def get_initial_message(self):
        """Get the initial greeting message"""
        # self.messages.append({"role": "user", "parts": [{"text": prompt.system_prompt}]})
        # self.messages.append({"role": "model", "parts": [{"text": "understand"}]})
        response, _, _ = await self.process_query("Hello", check_continue=False)
        return response.text

    def get_tools_info(self):
        """Get information about available tools"""
        if not self.tools:
            return None
        return self.tools

    async def cleanup(self):
        """Cleanup resources"""
        if self.mcp_client:
            try:
                await self.mcp_client.close()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

    
async def main():
    """Main function to run the MCP client"""
    client = MCPClient()
    connected = await client.connect_to_server()
    
    if not connected:
        return

    initial_message = await client.get_initial_message()
    print("Initial message:\n" + initial_message)

    while True:
        try:
            user_input = input("\nYou: ")
            await client.process_query_loop(user_input)

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())


