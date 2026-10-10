from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: Dict[str, Any] = Field(default_factory=dict)


class MCPContentItem(BaseModel):
    type: str = "text"
    text: str


class MCPCallToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


class MCPCallToolResult(BaseModel):
    content: List[MCPContentItem] = Field(default_factory=list)
    isError: bool = False


class MCPJsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    method: str
    params: Optional[Dict[str, Any]] = None


class MCPJsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Any] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
