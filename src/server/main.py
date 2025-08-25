from fastmcp import FastMCP
from file_operations_tools import register_tools
from data_analysis_tools import register_tools as data_reading_register_tools


# Initialize FastMCP server
mcp = FastMCP("Excel Data Reader 2")

# Register all tools
register_tools(mcp)
data_reading_register_tools(mcp)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport="http", host="127.0.0.1", port=9000)