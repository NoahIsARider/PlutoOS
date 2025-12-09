"""
Quick demo that runs PrivacyVault store/retrieve and a short collaboration exchange.
"""
import time
from Pluto.privacy import PrivacyVault
from Pluto.collab import CollabServer, CollabClient


def main():
    print('PlutoOS demo starting')
    v = PrivacyVault()
    v.store('greeting', 'Welcome to Pluto — privacy first'.encode('utf-8'))
    print('Stored greeting in vault')
    print('Retrieved:', v.retrieve('greeting').decode('utf-8'))

    srv = CollabServer()
    srv.start()
    print('Collab server started on port 6000')

    client = CollabClient()
    client.on_message = lambda m: print('[peer]', m)
    client.connect()
    client.send('Pluto says hello to peers')
    time.sleep(1)

    client.close()
    srv.stop()
    print('Demo finished')

if __name__ == '__main__':
    main()
