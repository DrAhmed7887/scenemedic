"""ClickHouse continuity DB, mounted as an MCP toolset for ADK."""
import os

from google.adk.tools.mcp_tool import MCPToolset, StdioServerParameters

clickhouse_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command="uvx",
        args=["mcp-clickhouse"],
        env={
            "CLICKHOUSE_HOST": os.getenv("CLICKHOUSE_URL", ""),
            "CLICKHOUSE_USER": os.getenv("CLICKHOUSE_USER", ""),
            "CLICKHOUSE_PASSWORD": os.getenv("CLICKHOUSE_PASSWORD", ""),
            "CLICKHOUSE_DATABASE": os.getenv("CLICKHOUSE_DATABASE", "scenemedic"),
        },
    ),
)
