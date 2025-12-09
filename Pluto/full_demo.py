"""
Automated full demo for Pluto userland "OS".
Runs through:
 - PrivacyVault (store/retrieve)
 - VFS (write/read/ls/rm)
 - Supervisor (register/start/status/stop)
 - Collab (server, two clients, send/receive)

Run via: `python -m Pluto.full_demo`
"""
import time
import queue

from Pluto.privacy import PrivacyVault
from Pluto.vfs import VFS
from Pluto.supervisor import Supervisor
from Pluto.collab import CollabServer, CollabClient
from Pluto.supervisor import Supervisor
import os


def demo_vault_and_vfs():
    print('== Vault & VFS demo ==')
    v = PrivacyVault()
    v.store('demo-secret', b'Pluto secret data')
    retrieved = v.retrieve('demo-secret')
    print('Vault retrieve:', retrieved)

    vfs = VFS()
    vfs.write('/notes/hello', b'Hello from Pluto VFS')
    print('VFS ls:', vfs.ls())
    data = vfs.read('/notes/hello')
    print('VFS read /notes/hello:', data)
    vfs.rm('/notes/hello')
    print('VFS after rm:', vfs.ls())


def demo_supervisor():
    print('\n== Supervisor demo ==')
    sup = Supervisor()
    # register the example worker service
    import sys
    worker_cmd = [sys.executable, '-u', '-m', 'Pluto.services.worker', '--name', 'demo-worker']
    sup.register_service('demo-worker', worker_cmd, restart=False)
    sup.start_service('demo-worker')
    time.sleep(2.5)
    st = sup.status()
    print('Supervisor status:', st)
    # print logs from service
    logs = st.get('demo-worker', {}).get('logs_tail', [])
    print('Service logs (tail):')
    for l in logs:
        print('  ', l)
    sup.stop_service('demo-worker')
    time.sleep(0.5)
    print('Supervisor status after stop:', sup.status())


def demo_collab():
    print('\n== Collaboration demo ==')
    # start server with TLS and token auth for demo
    os.makedirs('vault/ssl', exist_ok=True)
    certfile = 'vault/ssl/pluto-demo-cert.pem'
    keyfile = 'vault/ssl/pluto-demo-key.pem'
    srv = CollabServer(use_ssl=True, certfile=certfile, keyfile=keyfile, auth_token='secrettoken')
    srv.start()
    time.sleep(0.2)

    # prepare a queue to capture messages
    q = queue.Queue()

    c1 = CollabClient(use_ssl=True, token='secrettoken')
    c2 = CollabClient(use_ssl=True, token='secrettoken')

    c2.on_message = lambda m: q.put(m)

    c1.connect()
    c2.connect()
    time.sleep(0.2)

    msg = 'Hello peers from c1'
    print('c1 sending:', msg)
    c1.send(msg)

    # wait for message on c2
    try:
        received = q.get(timeout=3)
        print('c2 received:', received)
    except queue.Empty:
        print('c2 did not receive message (timeout)')

    c1.close()
    c2.close()
    srv.stop()


def main():
    print('Pluto full automated demo starting')
    demo_vault_and_vfs()
    demo_supervisor()
    demo_collab()
    print('\nPluto full demo finished')


if __name__ == '__main__':
    main()
