import asyncio
import json
from typing import Optional
import fastmcp
from fastmcp import Client, FastMCP
from google import genai
from google.genai import types

from dotenv import load_dotenv

load_dotenv()
MODEL = "gemini-2.5-flash"


class MCPClient:
    def __init__(self):
        # self.exit_stack = AsyncExitStack()
        self.gemini = genai.Client()


    async def connect_to_server(self, server_config):
        self.client = Client("http://127.0.0.1:9000/mcp")
        async with self.client:
            self.tools = await self.client.list_tools()
        self.messages = []

    def convert_tool_format(self, tool):
        converted_tool = {
            "name": tool.name,
            "description": tool.description,
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
            }
        }
        return converted_tool

    async def process_query(self, query: str) -> str:
        self.messages.append(
            types.Content(
                role="user", 
                parts=[types.Part(text=query)]
            )
        )

        available_tools = [self.convert_tool_format(tool) for tool in self.tools]
        tools = types.Tool(function_declarations=available_tools)
        config = types.GenerateContentConfig(tools=[tools])
        
        response = self.gemini.models.generate_content(
            model=MODEL,
            contents=self.messages,
            config=config,
        )

        while response.candidates[0].content.parts[0].function_call:
            tool_name = response.candidates[0].content.parts[0].function_call.name
            tool_args = response.candidates[0].content.parts[0].function_call.args
            try:
                print(f"Calling tool: {tool_name} with args: {tool_args}")

                async with self.client:
                    result = await self.client.call_tool(tool_name, tool_args)

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": result},
                )

                # Append function call and result of the function execution to contents
                self.messages.append(response.candidates[0].content) # Append the content from the model's response.
                self.messages.append(types.Content(role="user", parts=[function_response_part])) # Append the function response

            except Exception as e:
                print(f"Error calling tool {tool_name}: {e}")

            response = self.gemini.models.generate_content(
                model=MODEL,
                contents=self.messages,
                config=config,
            )

        return response.text

async def main():
    client = MCPClient()
    SERVER_CONFIG=None
    try:
        await client.connect_to_server(SERVER_CONFIG)
        print(await client.process_query("check what data exist and get all the columns of anyone of the data"))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    asyncio.run(main())
