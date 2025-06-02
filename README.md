# Alan MCP Project

A Python client and host implementation for the Multi-Component Protocol (MCP).

## Installation

You can install the `alan-mcp` package using pip:

```bash
pip install alan-mcp
```

(Note: For now, you'll need to build and install from a local wheel as it's not yet on PyPI. This instruction is for when it's published.)
To install from a local build:
```bash
pip install .
# or
# python -m build
# pip install dist/alan_mcp-*.whl
```

## Basic Usage

Here's a simple example of how to use the `alan-mcp` library:

```python
import asyncio
import json
import os
from alan_mcp.client import create_mcp_client_from_config
from alan_mcp.host import create_mcp_host_agent
from langchain_google_genai import ChatGoogleGenerativeAI # Or any other Langchain LLM

# --- Setup for Host (requires a running server) ---
async def run_host_example():
    # Create a dummy config for the host pointing to a local math server
    # Ensure math_server.py is executable and paths are correct
    # This example assumes you run it from the root of the project

    math_server_script_path = os.path.abspath("src/alan_mcp/simple_mcp_servers/math_server.py")
    if not os.path.exists(math_server_script_path):
        print(f"Math server script not found at {math_server_script_path}, skipping host example part.")
        return

    host_config_data = {
        "mcpServers": {
            "math": {
                "command": "python",
                "args": [math_server_script_path],
                "transport": "stdio"
            }
        }
    }
    host_config_file = "temp_host_config_for_readme.json"
    with open(host_config_file, 'w') as f:
        json.dump(host_config_data, f, indent=4)

    host_agent = None # Define host_agent here to be accessible in finally
    try:
        print("Initializing LLM...")
        # Make sure GOOGLE_API_KEY is set in your environment for Gemini
        # from dotenv import load_dotenv
        # load_dotenv()
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

        print(f"Creating MCP host agent with config: {host_config_file}...")
        host_agent = await create_mcp_host_agent(host_config_file, model=llm)
        print("Host agent created.")

        print("Invoking agent with: 'what is 10 + 5?'")
        response = await host_agent.ainvoke({"messages": [{"role": "user", "content": "what is 10 + 5?"}]})

        print("\nAgent Response:")
        for message in response.get("messages", []):
            message.pretty_print()

    except Exception as e:
        print(f"Error in host example: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if os.path.exists(host_config_file):
            os.remove(host_config_file)
        # Clean up any running servers if necessary (stdio transport should self-terminate)
        if host_agent and hasattr(host_agent, 'client') and hasattr(host_agent.client, 'close'):
            print("Closing host agent client...")
            await host_agent.client.close()


# --- Setup for Client (demonstrating client creation) ---
async def run_client_example():
    # Create a dummy config for the client
    # This example assumes you run it from the root of the project
    math_server_script_path = os.path.abspath("src/alan_mcp/simple_mcp_servers/math_server.py")
    if not os.path.exists(math_server_script_path):
        print(f"Math server script not found at {math_server_script_path}, skipping client example part.")
        return

    client_config_data = {
        "mcpServers": {
            "math": {
                "command": "python",
                "args": [math_server_script_path],
                "transport": "stdio"
            }
        }
    }
    client_config_file = "temp_client_config_for_readme.json"
    with open(client_config_file, 'w') as f:
        json.dump(client_config_data, f, indent=4)

    mcp_client = None # Define mcp_client here to be accessible in finally
    try:
        print(f"Creating MCP client with config: {client_config_file}...")
        mcp_client = create_mcp_client_from_config(client_config_file)
        print(f"MCP Client created: {mcp_client}")

        # To actually get tools, the server needs to be running.
        # This just shows client instantiation.
        print("Fetching tools (requires server to be running)...")
        tools = await mcp_client.get_tools()
        print(f"Available tools: {tools}")

    except Exception as e:
        print(f"Error in client example: {e}")
    finally:
        if os.path.exists(client_config_file):
            os.remove(client_config_file)
        if mcp_client and hasattr(mcp_client, 'close'):
             print("Closing mcp client...")
             await mcp_client.close()


async def main():
    # print("--- Running Client Example ---")
    # await run_client_example()
    # print("\n--- Running Host Example ---")
    # print("Note: The host example requires a Google API Key for the LLM.")
    # print("Ensure the .env file is configured or GOOGLE_API_KEY is in your environment.")
    await run_host_example() # Host example is more comprehensive

if __name__ == "__main__":
    # Nest asyncio if running in a Jupyter environment (common for Langchain users)
    try:
        import nest_asyncio
        nest_asyncio.apply()
    except ImportError:
        pass # Not a critical dependency for the core logic

    asyncio.run(main())
```
