import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


dotenv.load_dotenv()


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

async def main():
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Replace with absolute path to your math_server.py file
                "args": ["C:/Users\EST\PycharmProjects/alan-mcp/alan_mcp\math_mcp_tools.py"],
                "transport": "stdio",
            },
        }
    )
    print("MCP Client 생성")
    tools = await client.get_tools()
    print("MCP Tool 리스트 호출")
    agent = create_react_agent(
        llm,
        tools
    )
    print("Agent 생성")

    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    print("Math Response:", math_response)

if __name__ == "__main__":
    asyncio.run(main())