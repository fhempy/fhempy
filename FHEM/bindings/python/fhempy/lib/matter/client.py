"""Minimal client for the WebSocket API of the OHF Matter server.

The API is the same for the matter.js based server (npm package
matter-server) and the older Python Matter Server:
https://github.com/matter-js/matterjs-server
"""

import asyncio
import itertools
import json

import aiohttp


class MatterServerError(Exception):
    def __init__(self, error_code, details):
        super().__init__(details or f"Matter server error {error_code}")
        self.error_code = error_code


class MatterClient:
    def __init__(self, url, logger, on_event):
        self.url = url
        self.logger = logger
        self.server_info = {}
        self._on_event = on_event
        self._session = None
        self._ws = None
        self._ids = itertools.count(1)
        self._pending = {}

    @property
    def connected(self):
        return self._ws is not None and not self._ws.closed

    async def connect(self):
        """Connect, returns the list of nodes (start_listening)"""
        self._session = aiohttp.ClientSession()
        try:
            self._ws = await self._session.ws_connect(
                self.url, heartbeat=30, max_msg_size=0
            )
            # the server sends its server_info as first message
            msg = await self._ws.receive(timeout=10)
            if msg.type != aiohttp.WSMsgType.TEXT:
                raise ConnectionError("Matter server closed the connection")
            self.server_info = json.loads(msg.data)
        except BaseException:
            await self.close()
            raise

    async def listen(self):
        """Receive messages until the connection is closed"""
        try:
            async for msg in self._ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self._handle_message(json.loads(msg.data))
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.ERROR,
                ):
                    break
        finally:
            await self.close()

    async def _handle_message(self, msg):
        if "event" in msg:
            try:
                await self._on_event(msg["event"], msg.get("data"))
            except Exception:
                self.logger.exception(f"Failed to handle Matter event {msg['event']}")
            return
        future = self._pending.pop(msg.get("message_id"), None)
        if future is None or future.done():
            return
        if "error_code" in msg:
            future.set_exception(
                MatterServerError(msg["error_code"], msg.get("details"))
            )
        else:
            future.set_result(msg.get("result"))

    async def send_command(self, command, timeout=60, **args):
        if not self.connected:
            raise ConnectionError("Not connected to the Matter server")
        message_id = str(next(self._ids))
        future = asyncio.get_running_loop().create_future()
        self._pending[message_id] = future
        try:
            await self._ws.send_str(
                json.dumps({"message_id": message_id, "command": command, "args": args})
            )
            return await asyncio.wait_for(future, timeout)
        finally:
            self._pending.pop(message_id, None)

    async def close(self):
        for future in self._pending.values():
            if not future.done():
                future.set_exception(ConnectionError("Matter server disconnected"))
        self._pending.clear()
        if self._ws is not None:
            await self._ws.close()
        if self._session is not None:
            await self._session.close()
        self._ws = None
        self._session = None
