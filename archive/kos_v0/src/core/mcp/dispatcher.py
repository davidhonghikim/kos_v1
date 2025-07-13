from src.core.mcp.message_schema import Message

def dispatch(msg: Message):
    print(f"[MCP] Dispatching: {msg}")
    # Route to agent, plugin, or system service
