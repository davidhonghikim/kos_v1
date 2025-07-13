from src.core.mcp.dispatcher import dispatch
from src.core.mcp.message_schema import Message

def run_mcp():
    msg = Message(type="ping", content="MCP Online")
    dispatch(msg)
