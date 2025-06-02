import json
from langchain_mcp_adapters.client import MultiServerMCPClient

def create_mcp_client_from_config(config_file_path: str) -> MultiServerMCPClient:
    """
    Creates a MultiServerMCPClient instance from a JSON configuration file.

    Args:
        config_file_path: Path to the JSON configuration file.
                          The file should contain a key "mcpServers"
                          with a dictionary of server configurations.

    Returns:
        A MultiServerMCPClient instance.
    """
    with open(config_file_path, 'r') as f:
        config = json.load(f)
    
    mcp_servers_config = config.get("mcpServers")
    if not mcp_servers_config:
        raise ValueError("Configuration file must contain 'mcpServers' key with server configurations.")
        
    client = MultiServerMCPClient(mcp_servers_config)
    return client

if __name__ == '__main__':
    # Create a dummy config.json for testing
    dummy_config = {
        "mcpServers": {
            "math": {
                "command": "python",
                "args": ["./simple_mcp_servers/math_server.py"], # Replace with actual path if testing
                "transport": "stdio"
            }
        }
    }
    dummy_config_path = "dummy_config.json"
    with open(dummy_config_path, 'w') as f:
        json.dump(dummy_config, f, indent=4)

    print(f"Created dummy configuration file: {dummy_config_path}")
    
    # Example usage:
    try:
        # Assuming you have a 'docs/example_config.json' or you run this after creating dummy_config.json
        # client_instance = create_mcp_client_from_config("docs/example_config.json") 
        client_instance = create_mcp_client_from_config(dummy_config_path)
        print(f"Successfully created MultiServerMCPClient instance: {client_instance}")
        
        # Example: to get tools (requires servers to be running and accessible)
        # async def main():
        #     tools = await client_instance.get_tools()
        #     print(f"Available tools: {tools}")
        # import asyncio
        # asyncio.run(main())

    except FileNotFoundError:
        print(f"Error: Configuration file not found. Please create '{dummy_config_path}' or provide a valid path.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    # Clean up dummy file
    import os
    if os.path.exists(dummy_config_path):
        os.remove(dummy_config_path)
        print(f"Cleaned up dummy configuration file: {dummy_config_path}")


    import asyncio

    tools = asyncio.run(client_instance.get_tools())
    print(tools)