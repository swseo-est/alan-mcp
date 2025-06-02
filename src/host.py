from langgraph.prebuilt import create_react_agent
import asyncio
import json
import os
from langchain_core.language_models import BaseChatModel

# Assuming client.py is in the same directory or src is in PYTHONPATH
from client import create_mcp_client_from_config

async def create_mcp_host_agent(config_file_path: str, model: BaseChatModel = None):
    """
    Creates a LangGraph ReAct agent (referred to as "host") using tools
    configured via an MCP client, which is initialized from a config file.

    Args:
        config_file_path: Path to the JSON configuration file for MCP servers.
        model_name: The name of the language model to use for the ReAct agent.
                    Defaults to "anthropic:claude-3-7-sonnet-latest".

    Returns:
        An initialized ReAct agent instance.
    """
    print(f"Creating MCP client from config: {config_file_path}")
    mcp_client = create_mcp_client_from_config(config_file_path)
    
    print("Fetching tools from MCP client...")
    tools = await mcp_client.get_tools()
    print(f"Successfully fetched tools: {tools}")
    
    print(f"Creating ReAct agent")
    host_agent = create_react_agent(model, tools)
    print("Successfully created ReAct agent (host).")
    
    return host_agent

if __name__ == '__main__':
    from langchain_google_genai import ChatGoogleGenerativeAI
    from dotenv import load_dotenv

    load_dotenv()

    # Determine the path to the actual math_server.py
    # host.py is in src/, math_server.py is in src/simple_mcp_servers/
    host_py_dir = os.path.dirname(os.path.abspath(__file__))
    actual_math_server_path = os.path.normpath(os.path.join(host_py_dir, 'simple_mcp_servers', 'math_server.py'))

    # Check if the actual math_server.py exists
    if not os.path.exists(actual_math_server_path):
        print(f"Error: The math server script was not found at {actual_math_server_path}")
        print("Please ensure 'src/simple_mcp_servers/math_server.py' exists.")
        exit(1)
    
    print(f"Using actual math server: {actual_math_server_path}")

    dummy_config = {
        "mcpServers": {
            "math": {
                "command": "python",
                "args": [actual_math_server_path], 
                "transport": "stdio"
            }
            # Add other servers like weather if you have them running for testing
            # "weather": {
            #     "url": "http://localhost:8000/mcp", 
            #     "transport": "streamable_http"
            # }
        }
    }
    dummy_config_path = "dummy_host_config.json"
    with open(dummy_config_path, 'w') as f:
        json.dump(dummy_config, f, indent=4)
    print(f"Created temporary configuration file: {dummy_config_path}")

    async def main():
        host = None # Define host here to be accessible in finally
        try:
            print("Attempting to create host agent...")
            # Ensure math_server.py is executable (Python handles this on Windows if .py is associated)
            # On Linux/macOS, you might need: os.chmod(actual_math_server_path, 0o755)
            model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-04-17")

            host = await create_mcp_host_agent(dummy_config_path, model=model)
            print(f"Host agent created: {host}")

            # Actually use the agent with the math server
            print("Invoking agent with: 'what is 5 + 3?'")
            response = await host.ainvoke({"messages": [{"role": "user", "content": "what is 5 + 3?"}]})
            print(f"Agent response: {response}")

            for msg in response["messages"]:
               msg.pretty_print()

        except FileNotFoundError as e:
            print(f"Error: Configuration file or server script not found. {e}")
            print(f"Math server expected at: {actual_math_server_path}")
        except ValueError as e:
            print(f"ValueError: {e}")
        except Exception as e:
            print(f"An unexpected error occurred in main(): {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up dummy config file
            if os.path.exists(dummy_config_path):
                os.remove(dummy_config_path)
                print(f"Cleaned up temporary configuration file: {dummy_config_path}")
            
            # If the mcp_client in create_host_agent started background processes,
            # they might need to be explicitly stopped if they don't self-terminate.
            # For stdio transport, Python's subprocess management usually handles termination
            # when the client/main process exits or the client object is cleaned up,
            # but this depends on the langgraph and mcp-adapter internals.
            if host and hasattr(host, 'client') and hasattr(host.client, 'close'):
                 try:
                     print("Attempting to close MCP client...")
                     await host.client.close() # Assuming MultiServerMCPClient has an async close
                     print("MCP client closed.")
                 except Exception as e:
                     print(f"Error closing MCP client: {e}")


    asyncio.run(main())
