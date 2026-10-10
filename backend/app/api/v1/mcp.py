from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException

from ...models.mcp import (
    MCPTool,
    MCPCallToolRequest,
    MCPCallToolResult,
    MCPJsonRpcRequest,
    MCPJsonRpcResponse,
)
from ...services.mcp_server import mcp_server

router = APIRouter(prefix="/mcp", tags=["Official PayPal MCP Wallet Server"])


@router.get("/tools", response_model=List[MCPTool])
async def list_mcp_tools():
    """Lists official PayPal Model Context Protocol (MCP) wallet tools."""
    return mcp_server.get_tools()


@router.post("/tools/call", response_model=MCPCallToolResult)
async def call_mcp_tool(payload: MCPCallToolRequest):
    """Executes an MCP wallet tool under corporate guardrails."""
    res = await mcp_server.call_tool(payload.name, payload.arguments)
    return res


@router.post("/rpc", response_model=MCPJsonRpcResponse)
async def handle_mcp_jsonrpc(payload: MCPJsonRpcRequest):
    """JSON-RPC 2.0 endpoint for Claude Desktop, Cursor, and MCP clients."""
    return await mcp_server.handle_jsonrpc(payload)
