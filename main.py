import os
import asyncio
from dotenv import load_dotenv
from agents import Agent, Runner, trace
from contextlib import AsyncExitStack
from backend.mcp_servers.servers import (trader_mcp_servers, researcher_mcp_servers)

load_dotenv()

async def main():
    servers = trader_mcp_servers() + researcher_mcp_servers()

    # AsyncExitStack lauches all the servers and ensures they are properly closed when done.
    async with AsyncExitStack() as stack:
        for server in servers:
            await stack.enter_async_context(server)

        all_tools = []

        for server in servers:
            tools = await server.list_tools()
            all_tools.extend(tools)

        print(f"Loaded {len(all_tools)} tools from {len(servers)} servers.")

        agent = Agent(
            name="Financial Analyst",
            model="gpt-4o-mini",
            instructions="Answer financial-market questions using the "
                "Massive MCP tools. Use tools for current market data."
                "then use researcher MCP tools to get more information"
                "combine information from both Massive and researcher MCP tools to answer the question.",
            mcp_servers=servers,
        )

        with trace("Financial Analysis"):

            result = await Runner.run(
                agent,
                "Find information about Apple stock."
            )

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
