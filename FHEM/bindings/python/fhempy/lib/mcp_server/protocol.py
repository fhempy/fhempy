"""Model Context Protocol (MCP) server side, JSON-RPC 2.0 without transport.

Only the parts an AI app needs to use tools: initialize, ping, tools/list and
tools/call. The HTTP transport ("Streamable HTTP", answers as plain JSON, no
sessions) is in mcp_server.py.
"""

import json
import logging

from ..version import __version__

# newest first, an unknown version of the client gets the newest one
PROTOCOL_VERSIONS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


class ToolError(Exception):
    """Error which is shown to the AI as tool result, e.g. unknown device"""


class Tool:
    def __init__(
        self,
        name,
        description,
        handler,
        properties=None,
        required=(),
        title="",
        read_only=False,
        destructive=False,
    ):
        self.name = name
        self.description = description
        self.handler = handler
        self.properties = properties or {}
        self.required = list(required)
        self.title = title
        self.read_only = read_only
        self.destructive = destructive

    def definition(self):
        return {
            "name": self.name,
            "title": self.title or self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": self.properties,
                "required": self.required,
                "additionalProperties": False,
            },
            "annotations": {
                "title": self.title or self.name,
                "readOnlyHint": self.read_only,
                "destructiveHint": self.destructive,
                "idempotentHint": self.read_only,
                "openWorldHint": False,
            },
        }


def _error(msg_id, code, message):
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _result(msg_id, result):
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def tool_result(data, is_error=False):
    if isinstance(data, str):
        text = data
    else:
        text = json.dumps(data, ensure_ascii=False, indent=1)
    return {"content": [{"type": "text", "text": text}], "isError": is_error}


class McpServer:
    def __init__(self, name, instructions, tools_provider, logger=None):
        """tools_provider() returns the currently available tools, they
        depend on the attributes of the FHEM device"""
        self.name = name
        self.instructions = instructions
        self.tools_provider = tools_provider
        self.logger = logger or logging.getLogger(__name__)
        self.on_initialize = None

    def tools(self):
        return {tool.name: tool for tool in self.tools_provider()}

    async def handle(self, message):
        """Answer one JSON-RPC message, None for notifications and responses"""
        if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
            return _error(None, INVALID_REQUEST, "Invalid JSON-RPC message")
        method = message.get("method")
        msg_id = message.get("id")
        if method is None or "id" not in message:
            # notification (e.g. notifications/initialized) or a response
            return None
        params = message.get("params") or {}
        if not isinstance(params, dict):
            return _error(msg_id, INVALID_PARAMS, "params must be an object")
        try:
            if method == "initialize":
                return _result(msg_id, self.initialize(params))
            if method == "ping":
                return _result(msg_id, {})
            if method == "tools/list":
                tools = [tool.definition() for tool in self.tools().values()]
                return _result(msg_id, {"tools": tools})
            if method == "tools/call":
                return await self.call_tool(msg_id, params)
            return _error(msg_id, METHOD_NOT_FOUND, f"Method not found: {method}")
        except Exception:
            self.logger.exception(f"MCP request {method} failed")
            return _error(msg_id, INTERNAL_ERROR, "Internal error, see fhempy log")

    def initialize(self, params):
        requested = params.get("protocolVersion")
        version = requested if requested in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0]
        if self.on_initialize is not None:
            self.on_initialize(params.get("clientInfo") or {})
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": self.name, "title": "FHEM", "version": __version__},
            "instructions": self.instructions,
        }

    async def call_tool(self, msg_id, params):
        name = params.get("name")
        arguments = params.get("arguments") or {}
        tool = self.tools().get(name)
        if tool is None:
            return _error(msg_id, INVALID_PARAMS, f"Unknown tool: {name}")
        if not isinstance(arguments, dict):
            return _error(msg_id, INVALID_PARAMS, "arguments must be an object")
        missing = [arg for arg in tool.required if arguments.get(arg) in (None, "")]
        if missing:
            return _result(
                msg_id, tool_result(f"Missing argument: {', '.join(missing)}", True)
            )
        unknown = [arg for arg in arguments if arg not in tool.properties]
        if unknown:
            return _result(
                msg_id, tool_result(f"Unknown argument: {', '.join(unknown)}", True)
            )
        try:
            data = await tool.handler(**arguments)
        except ToolError as err:
            return _result(msg_id, tool_result(str(err), True))
        return _result(msg_id, tool_result(data))
