"""Certificates for a local https address of FHEMWEB.

Browsers offer notifications only on https pages with a trusted certificate.
fhempy creates a small certificate authority (CA) once, the phone trusts it
after a one-time installation. The certificate of FHEMWEB is signed by this
CA and can be renewed without installing anything on the phone again.
"""

import datetime
import ipaddress
import socket

# iOS accepts certificates of a trusted CA only up to 825 days
SERVER_DAYS = 825
CA_DAYS = 3650
RENEW_DAYS = 60


def _now():
    return datetime.datetime.now(datetime.timezone.utc)


def _name(common_name):
    from cryptography.x509.oid import NameOID
    from cryptography import x509

    return x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "fhempy"),
        ]
    )


def _new_key():
    from cryptography.hazmat.primitives.asymmetric import ec

    return ec.generate_private_key(ec.SECP256R1())


def key_pem(key):
    from cryptography.hazmat.primitives import serialization

    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()


def cert_pem(cert):
    from cryptography.hazmat.primitives import serialization

    return cert.public_bytes(serialization.Encoding.PEM).decode()


def load_key(pem):
    from cryptography.hazmat.primitives import serialization

    return serialization.load_pem_private_key(pem.encode(), password=None)


def load_cert(pem):
    from cryptography import x509

    return x509.load_pem_x509_certificate(pem.encode())


def create_ca(label):
    """returns (key, certificate) of a new CA"""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes

    key = _new_key()
    name = _name(f"fhempy {label}")
    now = _now()
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=CA_DAYS))
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(
            x509.SubjectKeyIdentifier.from_public_key(key.public_key()),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )
    return key, cert


def _alt_names(names):
    from cryptography import x509

    result = []
    for name in names:
        try:
            result.append(x509.IPAddress(ipaddress.ip_address(name)))
        except ValueError:
            result.append(x509.DNSName(name))
    return result


def create_server_cert(ca_key, ca_cert, names):
    """returns (key, certificate) for FHEMWEB, valid for all names"""
    from cryptography import x509
    from cryptography.x509.oid import ExtendedKeyUsageOID
    from cryptography.hazmat.primitives import hashes

    key = _new_key()
    now = _now()
    cert = (
        x509.CertificateBuilder()
        .subject_name(_name(names[0]))
        .issuer_name(ca_cert.subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=SERVER_DAYS))
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), True)
        .add_extension(x509.SubjectAlternativeName(_alt_names(names)), False)
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), False)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(ca_key.public_key()),
            False,
        )
        .sign(ca_key, hashes.SHA256())
    )
    return key, cert


def needs_renewal(cert, names):
    """True if the certificate expires soon or misses one of the names"""
    from cryptography import x509

    remaining = cert.not_valid_after_utc - _now()
    if remaining < datetime.timedelta(days=RENEW_DAYS):
        return True
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
    except x509.ExtensionNotFound:
        return True
    return bool(set(_alt_names(names)) - set(san.value))


def valid_hostname(name):
    """hostname or IP address the browser used, None if it is unusable"""
    name = str(name or "").strip().lower().strip("[]")
    if not name:
        return None
    try:
        return str(ipaddress.ip_address(name))
    except ValueError:
        pass
    labels = name.rstrip(".").split(".")
    if len(name) > 253 or not all(
        label
        and len(label) <= 63
        and label.replace("-", "").isalnum()
        and label.isascii()
        and not label.startswith("-")
        for label in labels
    ):
        return None
    return ".".join(labels)


def local_names():
    """hostname and IPv4 addresses of this computer in the home network"""
    import ifaddr

    names = []
    host = valid_hostname(socket.gethostname())
    if host and host != "localhost":
        names.append(host)
        if "." not in host:
            names.append(host + ".local")
    for adapter in ifaddr.get_adapters():
        for ip in adapter.ips:
            if not isinstance(ip.ip, str):
                continue
            address = ipaddress.ip_address(ip.ip)
            if address.is_private and not address.is_loopback:
                if not address.is_link_local and str(address) not in names:
                    names.append(str(address))
    return names
