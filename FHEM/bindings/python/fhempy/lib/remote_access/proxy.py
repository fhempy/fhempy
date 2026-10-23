"""Password protected proxy for web pages in the home network.

Web pages of ESPHome, Zigbee2MQTT... (FHEM weblinks to http://<home ip>:port)
are reachable via https://<name>.ts.net:<funnel port>. Every request needs
the password of the remote access: the proxy asks the FHEMWEB of the remote
access if the login (basic auth header or the AuthToken cookie FHEMWEB sets
after the login) is valid, so there is only one password.
"""

import asyncio
import hashlib
import time

AUTH_CACHE_SECONDS = 60
# hop-by-hop headers, not forwarded
HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def auth_token(cookie_header):
    """AuthToken cookie of the allowed device of FHEMWEB"""
    for part in (cookie_header or "").split(";"):
        name, _, value = part.strip().partition("=")
        if name == "AuthToken" and value:
            return value
    return None


def without_auth_cookie(cookie_header):
    parts = [
        p.strip()
        for p in (cookie_header or "").split(";")
        if p.strip() and not p.strip().startswith("AuthToken=")
    ]
    return "; ".join(parts)


class FhemwebLogin:
    """Checks logins with the FHEMWEB of the remote access"""

    def __init__(self, url_func):
        # url of FHEMWEB, e.g. http://127.0.0.1:8089
        self.url_func = url_func
        self._cache = {}
        self._protected_until = 0

    async def check(self, headers):
        """status of FHEMWEB for a request with these headers, None if
        FHEMWEB isn't reachable"""
        import aiohttp

        # a new connection for every check: FHEMWEB remembers a login per
        # connection
        connector = aiohttp.TCPConnector(force_close=True)
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            async with aiohttp.ClientSession(
                connector=connector, timeout=timeout
            ) as session:
                async with session.get(
                    self.url_func() + "/fhem/remote_access_login",
                    headers=headers,
                    allow_redirects=False,
                ) as resp:
                    return resp.status
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None

    def forget(self):
        """after a change of the password"""
        self._cache.clear()

    async def protected(self):
        """FHEMWEB must refuse requests without password, otherwise every
        login would look valid"""
        now = time.monotonic()
        if self._protected_until > now:
            return True
        if await self.check({}) != 401:
            return False
        self._protected_until = now + AUTH_CACHE_SECONDS
        return True

    async def valid(self, headers):
        auth = headers.get("Authorization")
        token = auth_token(headers.get("Cookie"))
        if not auth and not token:
            return False
        if not await self.protected():
            self._cache.clear()
            return False
        key = hashlib.sha256(f"{auth}\n{token}".encode()).hexdigest()
        now = time.monotonic()
        if self._cache.get(key, 0) > now:
            return True
        send = {"Authorization": auth} if auth else {"Cookie": f"AuthToken={token}"}
        status = await self.check(send)
        ok = status is not None and status != 401
        if ok:
            if len(self._cache) > 100:
                self._cache.clear()
            self._cache[key] = now + AUTH_CACHE_SECONDS
        return ok


class AuthProxy:
    """Forwards http and websocket requests to target after the login"""

    def __init__(self, target, login, logger):
        # e.g. http://192.168.1.10:6052
        self.target = target.rstrip("/")
        self.login = login
        self.logger = logger
        self.runner = None
        self.port = None
        self.session = None

    async def start(self):
        import aiohttp
        from aiohttp import web

        app = web.Application(client_max_size=64 * 1024 * 1024)
        app.router.add_route("*", "/{path:.*}", self.handle)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, "127.0.0.1", 0)
        await site.start()
        self.runner = runner
        self.port = site._server.sockets[0].getsockname()[1]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=None, sock_connect=10),
            auto_decompress=False,
        )
        return self.port

    async def stop(self):
        runner, self.runner = self.runner, None
        if runner is not None:
            await runner.cleanup()
        session, self.session = self.session, None
        if session is not None:
            await session.close()

    def forward_headers(self, request):
        headers = {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in HOP_HEADERS
            and k.lower() not in ("authorization", "cookie", "origin")
        }
        cookie = without_auth_cookie(request.headers.get("Cookie"))
        if cookie:
            headers["Cookie"] = cookie
        if "Origin" in request.headers:
            # the page in the home network accepts its own origin only
            headers["Origin"] = self.target
        return headers

    async def handle(self, request):
        from aiohttp import web

        if not await self.login.valid(request.headers):
            return web.Response(
                status=401,
                text="Login required",
                headers={"WWW-Authenticate": 'Basic realm="Login required"'},
            )
        url = self.target + request.rel_url.raw_path_qs
        if request.headers.get("Upgrade", "").lower() == "websocket":
            return await self.websocket(request, url)
        return await self.http(request, url)

    async def http(self, request, url):
        import aiohttp
        from aiohttp import web

        try:
            async with self.session.request(
                request.method,
                url,
                headers=self.forward_headers(request),
                data=request.content if request.can_read_body else None,
                allow_redirects=False,
            ) as resp:
                headers = {
                    k: v
                    for k, v in resp.headers.items()
                    if k.lower() not in HOP_HEADERS
                }
                location = headers.get("Location")
                if location and location.startswith(self.target):
                    headers["Location"] = location[len(self.target) :] or "/"
                answer = web.StreamResponse(status=resp.status, headers=headers)
                await answer.prepare(request)
                async for chunk in resp.content.iter_chunked(65536):
                    await answer.write(chunk)
                await answer.write_eof()
                return answer
        except aiohttp.ClientError as err:
            self.logger.debug(f"Proxy to {self.target} failed: {type(err).__name__}")
            return web.Response(status=502, text=f"{self.target} is not reachable")

    async def websocket(self, request, url):
        import aiohttp
        from aiohttp import web

        protocols = [
            p.strip()
            for p in request.headers.get("Sec-WebSocket-Protocol", "").split(",")
            if p.strip()
        ]
        try:
            upstream = await self.session.ws_connect(
                "ws" + url[4:],
                headers=self.forward_headers(request),
                protocols=protocols,
            )
        except (aiohttp.ClientError, aiohttp.WSServerHandshakeError) as err:
            self.logger.debug(
                f"Websocket to {self.target} failed: {type(err).__name__}"
            )
            return web.Response(status=502, text=f"{self.target} is not reachable")
        client = web.WebSocketResponse(
            protocols=[upstream.protocol] if upstream.protocol else ()
        )
        await client.prepare(request)

        async def pipe(src, dst):
            async for msg in src:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await dst.send_str(msg.data)
                elif msg.type == aiohttp.WSMsgType.BINARY:
                    await dst.send_bytes(msg.data)
                else:
                    break

        tasks = [
            asyncio.create_task(pipe(client, upstream)),
            asyncio.create_task(pipe(upstream, client)),
        ]
        try:
            await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        finally:
            for task in tasks:
                task.cancel()
            await upstream.close()
            await client.close()
        return client
