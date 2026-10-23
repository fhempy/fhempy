"""Web pages of the home network (ESPHome, Zigbee2MQTT...) via the remote access.

FHEM shows them with weblinks to <home ip>:<port> without https, which don't work
from outside and are insecure in the https page. Each of them gets an own
Funnel port (https://<name>.ts.net:8443, :10000) with a password protected
proxy (proxy.py), and the FHEMWEB of the remote access shows these addresses
instead of the home network ones.
"""

import ipaddress
import json
from urllib.parse import urlsplit, urlunsplit

from .. import fhem
from . import proxy

# Tailscale Funnel only allows these ports besides 443
FUNNEL_PORTS = (8443, 10000)
# these weblinks get the free ports first
PREFERRED_WEBLINKS = ("esphome_dashboard", "z2m_frontend")
HOME_DOMAINS = (".local", ".lan", ".home", ".fritz.box")


def home_origin(link):
    """scheme and <home ip>:<port> of a weblink without https as written in
    the link, None for other addresses"""
    try:
        url = urlsplit(str(link or "").strip())
        url.port
    except ValueError:
        return None
    host = url.hostname
    if url.scheme != "http" or not host or "@" in url.netloc:
        return None
    try:
        ip = ipaddress.ip_address(host)
        if not (ip.is_private or ip.is_loopback):
            return None
    except ValueError:
        # hostnames in the home network, e.g. raspberrypi or pi.local
        if "." in host and not host.endswith(HOME_DOMAINS):
            return None
    return urlunsplit((url.scheme, url.netloc, "", "", ""))


def assign_ports(weblinks):
    """{funnel port: (origin, [weblink names])} for the weblinks
    ({name: link}), the preferred ones first"""
    origins = {}
    order = sorted(
        weblinks,
        key=lambda n: (
            PREFERRED_WEBLINKS.index(n) if n in PREFERRED_WEBLINKS else 99,
            n.lower(),
        ),
    )
    for name in order:
        origin = home_origin(weblinks[name])
        if origin is not None:
            origins.setdefault(origin, []).append(name)
    return dict(zip(FUNNEL_PORTS, origins.items()))


def rewrite_command(web, mapping):
    """Perl: FHEMWEB web shows the addresses of mapping ({old: new}) in
    weblinks. The functions of weblink are wrapped once, FHEMWEB calls them
    with its name as first argument."""
    pairs = ", ".join(
        f"{fhem.perlString(k)} => {fhem.perlString(v)}" for k, v in mapping.items()
    )
    return (
        f"$data{{fhempy_remote_access}}{{{fhem.perlString(web)}}} = {{{pairs}}};"
        " if ($modules{weblink} && $modules{weblink}{LOADED}) {"
        " foreach my $fn ('FW_summaryFn', 'FW_detailFn') {"
        " my $orig = $modules{weblink}{$fn};"
        " next if (!$orig || ref($orig) eq 'CODE');"
        " $modules{weblink}{$fn} = sub { no strict 'refs';"
        " my $r = &{$orig}(@_);"
        " my $m = $data{fhempy_remote_access}{$_[0]};"
        " if ($m && defined($r)) { foreach my $from (keys %$m) {"
        " $r =~ s/\\Q$from\\E/$m->{$from}/g; } }"
        " return $r; }; } } ''"
    )


class Sites:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
        # origin -> AuthProxy
        self.proxies = {}
        # funnel port -> local proxy address
        self.exposed = {}
        self.mapping = None
        # "weblink: https://..." of the shared web pages
        self.shared = []
        self.login = proxy.FhemwebLogin(module.fhemweb_url)

    async def weblinks(self):
        result = await fhem.sendCommandHash(
            self.module.hash,
            "to_json({map { $_ => $defs{$_}{LINK} }"
            " grep { ($defs{$_}{WLTYPE} // '') =~ /^(iframe|link|image)$/ }"
            " devspec2array('TYPE=weblink')})",
        )
        try:
            links = json.loads(result)
        except (TypeError, ValueError):
            return {}
        return links if isinstance(links, dict) else {}

    async def update(self, dns):
        """Funnel ports and proxies for the current weblinks"""
        wanted = assign_ports(await self.weblinks())
        ts = self.module.ts
        for port in [p for p in self.exposed if p not in wanted]:
            await ts.funnel_port_off(port)
            del self.exposed[port]
        origins = {origin for origin, _ in wanted.values()}
        for origin in [o for o in self.proxies if o not in origins]:
            await self.proxies.pop(origin).stop()
        mapping = {}
        shared = []
        for port, (origin, names) in wanted.items():
            target = await self.proxy_address(origin)
            if self.exposed.get(port) != target:
                code, out = await ts.funnel_port(port, target)
                if code != 0:
                    self.logger.error(f"Funnel port {port} failed: {out}")
                    continue
                self.exposed[port] = target
            url = f"https://{dns}:{port}/"
            mapping[origin] = url[:-1]
            shared += [f"{name}: {url}" for name in names]
        if mapping != self.mapping:
            await fhem.sendCommandHash(
                self.module.hash, rewrite_command(self.module.web_name, mapping)
            )
            self.mapping = mapping
        self.shared = shared
        await fhem.readingsSingleUpdateIfChanged(
            self.module.hash, "web_pages", ", ".join(shared) or "none", 1
        )

    async def proxy_address(self, origin):
        if origin not in self.proxies:
            site = proxy.AuthProxy(origin, self.login, self.logger)
            await site.start()
            self.proxies[origin] = site
        # the proxy runs on this computer, Tailscale adds https
        return urlunsplit(
            ("http", f"127.0.0.1:{self.proxies[origin].port}", "", "", "")
        )

    async def stop(self):
        """Funnel ports are removed by `serve reset` of the next start"""
        self.exposed = {}
        self.mapping = None
        for site in self.proxies.values():
            await site.stop()
        self.proxies = {}
