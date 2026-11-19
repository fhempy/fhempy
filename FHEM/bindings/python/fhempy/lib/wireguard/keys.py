"""WireGuard keys (Curve25519, RFC 7748) without extra dependencies."""

import base64
import secrets

P = 2**255 - 19
A24 = 121665


def _clamp(key):
    k = bytearray(key)
    k[0] &= 248
    k[31] &= 127
    k[31] |= 64
    return int.from_bytes(k, "little")


def x25519(scalar, u_point):
    """RFC 7748 X25519 with 32 byte scalar and u coordinate"""
    k = _clamp(scalar)
    u = int.from_bytes(u_point, "little") & ((1 << 255) - 1)
    x_1, x_2, z_2, x_3, z_3, swap = u, 1, 0, u, 1, 0
    for t in reversed(range(255)):
        k_t = (k >> t) & 1
        swap ^= k_t
        if swap:
            x_2, x_3, z_2, z_3 = x_3, x_2, z_3, z_2
        swap = k_t
        a, b = (x_2 + z_2) % P, (x_2 - z_2) % P
        aa, bb = a * a % P, b * b % P
        e = (aa - bb) % P
        c, d = (x_3 + z_3) % P, (x_3 - z_3) % P
        da, cb = d * a % P, c * b % P
        x_3 = (da + cb) ** 2 % P
        z_3 = x_1 * (da - cb) ** 2 % P
        x_2 = aa * bb % P
        z_2 = e * (aa + A24 * e) % P
    if swap:
        x_2, z_2 = x_3, z_3
    return (x_2 * pow(z_2, P - 2, P) % P).to_bytes(32, "little")


def private_key():
    raw = bytearray(secrets.token_bytes(32))
    raw[0] &= 248
    raw[31] &= 127
    raw[31] |= 64
    return base64.b64encode(bytes(raw)).decode()


def public_key(private):
    raw = base64.b64decode(private)
    return base64.b64encode(x25519(raw, (9).to_bytes(32, "little"))).decode()


def preshared_key():
    return base64.b64encode(secrets.token_bytes(32)).decode()
