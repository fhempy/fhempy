"""MCP server: AI apps (Claude, LM Studio, ...) read and control FHEM.

The AI app connects to http://<fhempy ip>:<port>/mcp/<token> ("Streamable
HTTP" transport, plain JSON answers). Automations created by the AI stay
disabled until the user approves them, see tools.py for what the AI can do.
"""

import asyncio
import functools
import hmac
import html
import json
import secrets

from .. import fhem, generic, utils
from ..core import fhemweb
from . import protocol, tools

DEFAULT_PORT = 8099
MAX_REQUEST_SIZE = 1024 * 1024
ROOM_ICON = "it_server"
DEVICE_ICON = "it_server"
LOCAL_HOSTS = ("localhost", "127.0.0.1", "::1", "[::1]")

DEVICES_HELP = (
    "Only these devices are visible for the AI, e.g. room=Livingroom,"
    "Kitchen or TYPE=HUEDevice. Empty: all devices. Automations (DOIF, "
    "notify, at, watchdog) are always visible."
)
HIDDEN_HELP = (
    "These devices are never visible for the AI, e.g. Alarm_system,"
    "TYPE=Calendar. FHEM internals (FHEMWEB, logs, fhempy) are always hidden."
)
APPROVAL_HELP = (
    "1 (recommended): automations created or changed by the AI stay "
    "disabled until you approve them here. 0: they are active immediately."
)
COMMAND_HELP = (
    "1: the AI may run any FHEM command, e.g. change attributes or delete "
    "devices. It can also read passwords stored in FHEM then. Only switch "
    "this on if you know what you are doing."
)


def rpc_error(status, message, code=protocol.INVALID_REQUEST):
    from aiohttp import web

    return web.json_response(
        {"jsonrpc": "2.0", "id": None, "error": {"code": code, "message": message}},
        status=status,
    )


class mcp_server(generic.FhemModule):
    def __init__(self, logger):
        super().__init__(logger)
        self.tools = tools.FhemTools(self)
        self.server = protocol.McpServer("fhem", "", self.tools.tools, logger)
        self.server.on_initialize = self.on_initialize
        self.runner = None
        self._server_lock = asyncio.Lock()
        self.token = ""
        self.ip = "127.0.0.1"
        self.created = []
        self.pending = []
        # name -> type, definition, comment of the pending automations
        self.pending_info = {}
        self._unique_id = None

    # FHEM FUNCTION
    async def Define(self, hash, args, argsh):
        self.hash = hash
        await super().Define(hash, args, argsh)
        attr_config = {
            "port": {
                "default": str(DEFAULT_PORT),
                "format": "int",
                "help": f"Network port of the MCP server, default {DEFAULT_PORT}. "
                "Change it only if the port is used by another program.",
            },
            "devices": {"default": "", "help": DEVICES_HELP},
            "hidden_devices": {"default": "", "help": HIDDEN_HELP},
            "allow_set": {
                "default": "1",
                "format": "int",
                "options": "0,1",
                "help": "1: the AI may switch devices (on, off, pct 50...). "
                "0: it can only read.",
            },
            "allow_automations": {
                "default": "1",
                "format": "int",
                "options": "0,1",
                "help": "1: the AI may create automations (DOIF, notify, at, "
                "watchdog). It can only change and delete automations it "
                "created itself.",
            },
            "require_approval": {
                "default": "1",
                "format": "int",
                "options": "0,1",
                "help": APPROVAL_HELP,
            },
            "automation_room": {
                "default": "AI",
                "help": "Room of the automations created by the AI, default AI.",
            },
            "allow_fhem_command": {
                "default": "0",
                "format": "int",
                "options": "0,1",
                "help": COMMAND_HELP,
            },
        }
        await self.set_attr_config(attr_config)
        self._unique_id = await fhem.getUniqueId(hash)
        await self.load_state()
        await self.update_set_config()
        await fhemweb.setup_room(
            hash, self._attr_automation_room, ROOM_ICON, DEVICE_ICON
        )
        self.ip = await utils.run_blocking(functools.partial(utils.get_local_ip))
        await self.start_server()

    # FHEM FUNCTION
    async def Undefine(self, hash):
        await self.stop_server()
        await super().Undefine(hash)

    # FHEM FUNCTION
    async def FW_detailFn(self, hash, args, argsh):
        # FHEM doesn't answer commands while it waits for the detail page,
        # the definitions of the pending automations are read before
        detail = await super().FW_detailFn(hash, args, argsh)
        pending = [self.pending_info.get(n, {"name": n}) for n in self.pending]
        return self.setup_html(pending) + str(detail)

    async def update_pending_info(self):
        if not self.pending:
            self.pending_info = {}
            return
        names_perl = ",".join(fhem.perlString(n) for n in self.pending)
        result = await fhem.sendCommandHash(
            self.hash,
            "to_json([map { {name => $_, type => $defs{$_}{TYPE},"
            " definition => $defs{$_}{DEF} // '',"
            " comment => AttrVal($_, 'comment', '')} }"
            f" grep {{ defined($defs{{$_}}) }} ({names_perl})])",
        )
        try:
            self.pending_info = {info["name"]: info for info in json.loads(result)}
        except (TypeError, ValueError, KeyError):
            self.logger.error(f"Failed to read automations: {result}")

    # --- state ---

    async def load_state(self):
        name = self.hash["NAME"]
        token = await fhem.ReadingsVal(name, ".token", "")
        if token:
            try:
                self.token = utils.decrypt_string(token, self._unique_id)
            except Exception:
                self.token = ""
        if not self.token:
            await self.new_token()
        self.created = self._split(await fhem.ReadingsVal(name, ".created", ""))
        self.pending = self._split(await fhem.ReadingsVal(name, ".pending", ""))
        await self.update_pending_info()

    @staticmethod
    def _split(value):
        return [v for v in str(value or "").split(",") if v]

    async def new_token(self):
        self.token = secrets.token_urlsafe(24)
        await fhem.readingsSingleUpdate(
            self.hash, ".token", utils.encrypt_string(self.token, self._unique_id), 0
        )

    async def save_lists(self):
        await self.update_pending_info()
        await fhem.readingsBeginUpdate(self.hash)
        await fhem.readingsBulkUpdate(self.hash, ".created", ",".join(self.created))
        await fhem.readingsBulkUpdate(self.hash, ".pending", ",".join(self.pending))
        await fhem.readingsBulkUpdate(
            self.hash, "waiting_for_approval", ",".join(self.pending) or "none"
        )
        await fhem.readingsEndUpdate(self.hash, 1)
        await self.update_state()
        await self.update_set_config()

    async def update_state(self, error=None):
        if error:
            state = f"error: {error}"
        elif self.runner is None:
            state = "stopped"
        elif self.pending:
            state = f"waiting for approval: {', '.join(self.pending)}"
        else:
            state = "ready"
        await fhem.readingsSingleUpdateIfChanged(self.hash, "state", state, 1)

    async def add_created(self, name, needs_approval):
        if name not in self.created:
            self.created.append(name)
        if needs_approval and name not in self.pending:
            self.pending.append(name)
        if not needs_approval and name in self.pending:
            self.pending.remove(name)
        await self.save_lists()

    async def forget(self, name):
        changed = False
        for names in (self.created, self.pending):
            if name in names:
                names.remove(name)
                changed = True
        if changed:
            await self.save_lists()

    async def forget_missing(self, names=None):
        """remove automations which were deleted in FHEM from the lists"""
        if not self.created:
            return
        names_perl = ",".join(fhem.perlString(n) for n in self.created)
        result = await fhem.sendCommandHash(
            self.hash, f"join(',', grep {{ defined($defs{{$_}}) }} ({names_perl}))"
        )
        if not isinstance(result, str) or result.startswith("Exception"):
            return
        existing = self._split(result)
        missing = [n for n in self.created if n not in existing]
        for name in missing:
            await self.forget(name)

    async def log_action(self, action):
        self.logger.info(f"AI: {action}")
        await fhem.readingsSingleUpdate(self.hash, "last_action", action, 1)

    def on_initialize(self, client_info):
        client = " ".join(
            str(client_info.get(k, "")) for k in ("name", "version")
        ).strip()
        if client:
            self.create_async_task(
                fhem.readingsSingleUpdateIfChanged(self.hash, "last_client", client, 1)
            )

    # --- set commands ---

    def set_config(self):
        config = {
            "new_token": {
                "help": "Create a new secret address. The old address stops "
                "working, enter the new one in your AI apps."
            },
        }
        if self.pending:
            options = ",".join(self.pending + ["all"])
            config["approve"] = {
                "args": ["automation"],
                "options": options,
                "help": "Activate an automation created by the AI. Check its "
                "definition on this page first.",
            }
            config["reject"] = {
                "args": ["automation"],
                "options": options,
                "help": "Delete an automation created by the AI.",
            }
        return config

    async def update_set_config(self):
        await self.set_set_config(self.set_config())

    async def set_new_token(self, hash, params):
        await self.new_token()
        await fhem.readingsSingleUpdate(self.hash, "last_action", "new address", 1)

    async def set_approve(self, hash, params):
        names = self._selected(params["automation"])
        for name in names:
            await fhem.CommandDeleteAttr(self.hash, f"{name} disable")
            self.logger.info(f"Approved automation {name}")
            if name in self.pending:
                self.pending.remove(name)
        await self.forget_missing()
        await self.save_lists()

    async def set_reject(self, hash, params):
        for name in self._selected(params["automation"]):
            self.logger.info(f"Rejected automation {name}")
            await self.delete_automation(name)

    def _selected(self, name):
        if name == "all":
            return list(self.pending)
        if name not in self.pending:
            raise ValueError(f"{name} is not waiting for approval")
        return [name]

    async def Set(self, hash, args, argsh):
        try:
            return await super().Set(hash, args, argsh)
        except ValueError as err:
            return str(err)

    async def delete_automation(self, name):
        """delete an automation of the AI, only DOIF, notify, at, watchdog in
        case somebody defined another device with the same name meanwhile"""
        result = await fhem.sendCommandHash(
            self.hash,
            f"my $n = {fhem.perlString(name)};"
            " return 'missing' if (!defined($defs{$n})"
            f" || $defs{{$n}}{{TYPE}} !~ /^(?:{'|'.join(tools.AUTOMATION_TYPES)})$/);"
            " CommandDelete(undef, $n) // ''",
        )
        await self.forget(name)
        return result != "missing"

    # --- attributes ---

    async def set_attr_port(self, hash):
        # in the background, FHEM waits for the answer of Attr
        self.create_async_task(self.start_server())

    async def set_attr_require_approval(self, hash):
        self.server.instructions = self.instructions()

    def instructions(self):
        return tools.instructions(self.hash["NAME"], bool(self._attr_require_approval))

    # --- HTTP server ---

    def url(self, with_token=True):
        # plain http: the server runs in the home network without certificate
        url = f"http://{self.ip}:{self._attr_port}/mcp"  # NOSONAR
        return f"{url}/{self.token}" if with_token else url

    async def start_server(self):
        """(re)start the HTTP server, also on a change of attribute port"""
        async with self._server_lock:
            await self.stop_server()
            await self._start_server()

    async def _start_server(self):
        from aiohttp import web

        self.server.instructions = self.instructions()
        app = web.Application(client_max_size=MAX_REQUEST_SIZE)
        app.router.add_route("*", "/mcp", self.handle_http)
        app.router.add_route("*", "/mcp/{token}", self.handle_http)
        app.router.add_get("/", self.handle_root)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        try:
            site = web.TCPSite(runner, port=self._attr_port)
            await site.start()
        except OSError as err:
            await runner.cleanup()
            self.logger.error(f"MCP server can't use port {self._attr_port}: {err}")
            await self.update_state(
                f"port {self._attr_port} is used by another program, "
                "change attribute port"
            )
            return
        self.runner = runner
        self.logger.info(f"MCP server listening on {self.url(False)}")
        await fhem.readingsSingleUpdateIfChanged(self.hash, "url", self.url(False), 1)
        await self.update_state()

    async def stop_server(self):
        runner, self.runner = self.runner, None
        if runner is not None:
            await runner.cleanup()

    def authorized(self, request):
        token = request.match_info.get("token")
        if token is None:
            header = request.headers.get("Authorization", "")
            if header[:7].lower() == "bearer ":
                token = header[7:].strip()
        if not token or not self.token:
            return False
        return hmac.compare_digest(token.encode(), self.token.encode())

    @staticmethod
    def origin_allowed(request):
        """Browsers send Origin, a web page in the LAN must not use the
        server (DNS rebinding). AI apps don't send it."""
        from yarl import URL

        origin = request.headers.get("Origin")
        if not origin:
            return True
        try:
            host = URL(origin).host
        except ValueError:
            return False
        return host in LOCAL_HOSTS or host == request.url.host

    async def handle_root(self, request):
        from aiohttp import web

        return web.Response(
            text="FHEM MCP server (fhempy). Enter the address shown on the "
            "FHEM device page in your AI app.\n"
        )

    async def handle_http(self, request):
        from aiohttp import web

        if not self.origin_allowed(request):
            return rpc_error(403, "Origin not allowed")
        if not self.authorized(request):
            return rpc_error(
                401,
                "Wrong or missing token, use the address shown on the FHEM "
                "device page",
            )
        if request.method == "GET" and "text/event-stream" not in request.headers.get(
            "Accept", ""
        ):
            # somebody opened the address in a browser
            return web.Response(
                text="This address works. Enter it in your AI app as MCP server "
                "(type 'Streamable HTTP').\n"
            )
        if request.method != "POST":
            # no server sent events and no sessions
            return web.Response(status=405, headers={"Allow": "POST"})
        try:
            body = json.loads(await request.read())
        except web.HTTPRequestEntityTooLarge:
            return rpc_error(413, "Request too large")
        except (ValueError, UnicodeDecodeError):
            return rpc_error(400, "Invalid JSON", protocol.PARSE_ERROR)
        if isinstance(body, list):
            if not body:
                return rpc_error(400, "Empty batch")
            answers = [await self.server.handle(m) for m in body]
            answers = [a for a in answers if a is not None]
        else:
            answers = await self.server.handle(body)
        if not answers:
            # only notifications, e.g. notifications/initialized
            return web.Response(status=202)
        return web.json_response(
            answers, dumps=lambda d: json.dumps(d, ensure_ascii=False)
        )

    # --- FHEMWEB page ---

    def setup_html(self, pending=()):
        if not hasattr(self, "hash"):
            return ""
        name = html.escape(self.hash["NAME"])
        url = html.escape(self.url())
        desktop = html.escape(
            json.dumps(
                {
                    "mcpServers": {
                        "fhem": {
                            "command": "npx",
                            "args": ["-y", "mcp-remote", self.url(), "--allow-http"],
                        }
                    }
                },
                indent=2,
            )
        )
        code_cmd = html.escape(f"claude mcp add --transport http fhem {self.url()}")
        box = 'style="width:100%;box-sizing:border-box;font-family:monospace"'
        if self.runner is None:
            status = (
                "<b style='color:#c00'>The MCP server is not running, see "
                "reading state.</b><br><br>"
            )
        else:
            status = ""
        parts = [
            '<div class="makeTable wide">'
            '<span class="mkTitle">Connect your AI app</span>',
            '<table class="block wide"><tr class="odd"><td>',
            status,
            "<b>1. Your secret address</b> (like a password, don't share it):<br>",
            f'<input type="text" readonly value="{url}" {box}'
            ' onclick="this.select()"><br><br>',
            "<b>2. Enter it in your AI app</b><br>",
            "<details><summary><b>Claude Desktop</b> (needs "
            '<a href="https://nodejs.org" target="_blank">Node.js</a> on your '
            "computer)</summary>Settings &rarr; Developer &rarr; Edit Config, "
            "paste this into the file, save it and restart Claude Desktop:"
            f'<textarea readonly rows="10" {box} onclick="this.select()">{desktop}'
            "</textarea></details>",
            "<details><summary><b>Claude Code</b></summary>Run in a terminal:"
            f'<input type="text" readonly value="{code_cmd}" {box} '
            'onclick="this.select()"></details>',
            "<details><summary><b>LM Studio, Cursor, VS Code, n8n and other "
            "apps</b></summary>Add an MCP server of type <i>Streamable HTTP</i> "
            "(sometimes just <i>HTTP</i> or <i>URL</i>) with the address above."
            "</details><br>",
            "<b>3. Ask the AI</b>, e.g. <i>&quot;Which lights are on?&quot;</i> "
            "or <i>&quot;Switch off all lights when I leave the house.&quot;</i><br>",
            "Automations created by the AI wait for your approval below "
            "(attribute require_approval).",
            "</td></tr></table></div>",
        ]
        if pending:
            parts.append(self.pending_html(name, pending))
        return "".join(parts)

    def pending_html(self, name, pending):
        rows = []
        for i, info in enumerate(pending):
            auto = html.escape(info["name"])
            cls = "odd" if i % 2 == 0 else "even"
            comment = str(info.get("comment") or "")
            if comment.startswith("AI: "):
                comment = comment[4:]

            def button(cmd, label):
                js = (
                    "FW_cmd(FW_root+'?cmd='+encodeURIComponent('set "
                    f"{name} {cmd} {auto}')+'&amp;XHR=1',"
                    "function(){location.reload()});"
                    "return false;"
                )
                return f'<a href="#" onclick="{js}">{label}</a>'

            rows.append(
                f'<tr class="{cls}"><td style="vertical-align:top">'
                f'<a href="?detail={auto}"><b>{auto}</b></a><br>'
                f'{html.escape(str(info.get("type") or ""))}</td><td>'
                f"{html.escape(comment)}"
                '<pre style="white-space:pre-wrap;margin:4px 0">'
                f'{html.escape(str(info.get("definition") or ""))}</pre>'
                f'{button("approve", "Approve")} &nbsp; '
                f'{button("reject", "Reject")}</td></tr>'
            )
        return (
            '<div class="makeTable wide"><span class="mkTitle">Waiting for '
            "your approval</span>"
            '<table class="block wide"><tr class="odd"><td colspan="2">'
            "The AI created these automations. They do nothing until you "
            "approve them, check what they do first.</td></tr>"
            + "".join(rows)
            + "</table></div>"
        )
