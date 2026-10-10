#!/usr/bin/env python3
"""PayAgent OS — Official PayPal MCP Stdio Bridge
Allows Claude Desktop, Cursor IDE, and MCP clients to connect directly to PayAgent OS
via stdio (standard input/output) JSON-RPC 2.0 protocol.

Usage in claude_desktop_config.json:
{
  "mcpServers": {
    "payagent-os": {
      "command": "python",
      "args": ["c:/projects/paypal-ai-hackathon/backend/mcp_stdio_bridge.py"]
    }
  }
}
"""

import sys
import json
import asyncio
from typing import Optional

# Ensure project root is in sys.path
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.models.mcp import MCPJsonRpcRequest
from backend.app.services.mcp_server import mcp_server


async def main():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        raw_text = line.decode("utf-8").strip()
        if not raw_text:
            continue

        try:
            req_data = json.loads(raw_text)
            rpc_req = MCPJsonRpcRequest(**req_data)
            rpc_res = await mcp_server.handle_jsonrpc(rpc_req)
            out_json = json.dumps(rpc_res.model_dump(exclude_none=True))
            sys.stdout.write(out_json + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_res = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)},
            }
            sys.stdout.write(json.dumps(err_res) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(main())
