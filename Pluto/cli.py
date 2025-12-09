"""
Command-line interface for Pluto demo.
Usage:
  - Start server: `python3 -m Pluto.cli --server`
  - Start client: `python3 -m Pluto.cli --client --send "hello"`
  - Demo: `python3 -m Pluto.cli --demo`
"""
import argparse
import time
from Pluto.privacy import PrivacyVault
from Pluto.collab import CollabServer, CollabClient
from Pluto.kernel import Kernel


def run_server(port=6000):
    srv = CollabServer(port=port)
    srv.start()
    print(f"Pluto Collab Server listening on 127.0.0.1:{port}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()


def run_client(host='127.0.0.1', port=6000, send=None):
    c = CollabClient(host=host, port=port)
    c.on_message = lambda m: print(f"[remote] {m}")
    c.connect()
    if send:
        c.send(send)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        c.close()


def demo():
    print('Starting Pluto demo...')
    # privacy demo
    v = PrivacyVault()
    v.store('secret', b'Pluto keeps your secrets safe')
    print('Stored secret into vault')
    print('Retrieving secret:', v.retrieve('secret'))

    # collaboration demo
    srv = CollabServer()
    srv.start()
    print('Started collab server on port 6000')

    client = CollabClient()
    client.on_message = lambda m: print('[peer]', m)
    client.connect()
    client.send('Hello from Pluto client')
    time.sleep(1)
    srv.stop()
    client.close()
    print('Demo finished')

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--server', action='store_true')
    p.add_argument('--client', action='store_true')
    p.add_argument('--send')
    p.add_argument('--demo', action='store_true')
    args = p.parse_args()
    if args.server:
        run_server()
    elif args.client:
        run_client(send=args.send)
    elif args.demo:
        demo()
    else:
        p.print_help()
