"""
Collaboration module — simple TCP-based server and client for peer messages.
Demonstrates coordination and messaging between PlutoOS peers.
"""
import socket
import threading
import ssl
import os
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.serialization import NoEncryption
from cryptography.hazmat.backends import default_backend
import datetime

class CollabServer:
    def __init__(self, host='127.0.0.1', port=6000, use_ssl=False, certfile=None, keyfile=None, auth_token=None):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.certfile = certfile
        self.keyfile = keyfile
        self.auth_token = auth_token
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.lock = threading.Lock()
        self._running = False
        self._ssl_context = None
        if self.use_ssl:
            # ensure cert/key exist; generate self-signed if files missing or not provided
            os.makedirs('vault/ssl', exist_ok=True)
            if not self.certfile:
                self.certfile = 'vault/ssl/pluto-cert.pem'
            if not self.keyfile:
                self.keyfile = 'vault/ssl/pluto-key.pem'
            if not (os.path.exists(self.certfile) and os.path.exists(self.keyfile)):
                self._generate_self_signed(self.certfile, self.keyfile)
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ctx.load_cert_chain(self.certfile, self.keyfile)
            self._ssl_context = ctx

    def _generate_self_signed(self, certfile: str, keyfile: str, common_name: str = 'PlutoLocal'):
        # generate RSA key
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())
        # subject / issuer
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"Pluto"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"PlutoOS"),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        cert = x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(
            key.public_key()
        ).serial_number(x509.random_serial_number()).not_valid_before(
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(common_name)]), critical=False,
        ).sign(key, hashes.SHA256(), default_backend())

        # write key
        with open(keyfile, 'wb') as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        # write cert
        with open(certfile, 'wb') as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self._running = True
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while self._running:
            try:
                conn, addr = self.sock.accept()
                # wrap with SSL if enabled
                if self._ssl_context:
                    try:
                        conn = self._ssl_context.wrap_socket(conn, server_side=True)
                    except Exception:
                        conn.close()
                        continue
                with self.lock:
                    self.clients.append(conn)
                threading.Thread(target=self._client_loop, args=(conn, addr), daemon=True).start()
            except Exception:
                pass

    def _client_loop(self, conn, addr):
        try:
            with conn:
                # first message may be auth token if server expects it
                if self.auth_token:
                    raw = conn.recv(4096)
                    if not raw:
                        return
                    token = raw.decode().strip()
                    if token != self.auth_token:
                        try:
                            conn.sendall(b'ERR auth')
                        except Exception:
                            pass
                        return
                while True:
                    raw = conn.recv(4096)
                    if not raw:
                        break
                    msg = raw.decode()
                    self.broadcast(msg, exclude=conn)
        finally:
            with self.lock:
                if conn in self.clients:
                    self.clients.remove(conn)

    def broadcast(self, msg, exclude=None):
        with self.lock:
            for c in list(self.clients):
                if c is exclude:
                    continue
                try:
                    c.sendall(msg.encode())
                except Exception:
                    try:
                        c.close()
                    except:
                        pass
                    if c in self.clients:
                        self.clients.remove(c)

    def stop(self):
        self._running = False
        try:
            self.sock.close()
        except Exception:
            pass
        with self.lock:
            for c in self.clients:
                try:
                    c.close()
                except Exception:
                    pass
            self.clients = []

class CollabClient:
    def __init__(self, host='127.0.0.1', port=6000, use_ssl=False, cafile=None, token=None):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.cafile = cafile
        self.token = token
        self.sock = None
        self._recv_thread = None
        self.on_message = None

    def connect(self):
        raw = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        raw.connect((self.host, self.port))
        if self.use_ssl:
            ctx = ssl.create_default_context()
            if self.cafile:
                ctx.load_verify_locations(self.cafile)
            else:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            self.sock = ctx.wrap_socket(raw, server_hostname=self.host)
        else:
            self.sock = raw

        # send auth token first if provided
        if self.token:
            try:
                self.sock.sendall(self.token.encode())
            except Exception:
                pass

        self._recv_thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._recv_thread.start()

    def _recv_loop(self):
        while True:
            try:
                raw = self.sock.recv(4096)
                if not raw:
                    break
                if self.on_message:
                    self.on_message(raw.decode())
            except Exception:
                break

    def send(self, msg: str):
        if self.sock:
            self.sock.sendall(msg.encode())

    def close(self):
        try:
            self.sock.close()
        except Exception:
            pass
