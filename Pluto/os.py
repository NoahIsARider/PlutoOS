"""
Pluto OS userland entrypoint. Starts supervisor, registers example services and launches shell.
"""
import sys
import os
from Pluto.supervisor import Supervisor
from Pluto.vfs import VFS
from Pluto.shell import Shell


def main():
    sup = Supervisor()
    # register an example worker service (module)
    py = sys.executable
    worker_cmd = [py, '-m', 'Pluto.services.worker', '--name', 'pluto-worker']
    sup.register_service('pluto-worker', worker_cmd, restart=True)

    vfs = VFS()

    # start core services
    sup.start_all()

    shell = Shell(sup, vfs)
    try:
        shell.run()
    finally:
        sup.stop_all()


if __name__ == '__main__':
    main()
