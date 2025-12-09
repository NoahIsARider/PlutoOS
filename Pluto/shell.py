"""
Interactive Shell for Pluto userland OS.
Commands: help, services, start <name>, stop <name>, status, ls, cat, write <path>, rm <path>, exit
"""
import sys
import shlex
from Pluto.supervisor import Supervisor
from Pluto.vfs import VFS


class Shell:
    def __init__(self, supervisor: Supervisor, vfs: VFS):
        self.sup = supervisor
        self.vfs = vfs

    def run(self):
        print('Pluto Shell — type "help" for commands')
        while True:
            try:
                raw = input('pluto> ')
            except EOFError:
                print()
                break
            if not raw.strip():
                continue
            args = shlex.split(raw)
            cmd = args[0]
            try:
                if cmd == 'help':
                    self._help()
                elif cmd == 'services':
                    print('\n'.join(self.sup.status().keys()))
                elif cmd == 'start' and len(args) > 1:
                    self.sup.start_service(args[1])
                elif cmd == 'stop' and len(args) > 1:
                    self.sup.stop_service(args[1])
                elif cmd == 'status':
                    import json
                    print(json.dumps(self.sup.status(), indent=2))
                elif cmd == 'ls':
                    pref = args[1] if len(args) > 1 else ''
                    for f in self.vfs.ls(pref):
                        print(f)
                elif cmd == 'cat' and len(args) > 1:
                    print(self.vfs.read(args[1]).decode('utf-8'))
                elif cmd == 'write' and len(args) > 2:
                    path = args[1]
                    data = ' '.join(args[2:]).encode('utf-8')
                    self.vfs.write(path, data)
                elif cmd == 'rm' and len(args) > 1:
                    self.vfs.rm(args[1])
                elif cmd == 'exit':
                    break
                else:
                    print('Unknown or malformed command. Type help.')
            except Exception as e:
                print('Error:', e)

    def _help(self):
        print('Commands:')
        print('  help                     Show this help')
        print('  services                 List registered services')
        print('  start <name>             Start a service')
        print('  stop <name>              Stop a service')
        print('  status                   Show status of services')
        print('  ls [prefix]              List VFS entries')
        print('  cat <path>               Read VFS file')
        print('  write <path> <content>   Write VFS file')
        print('  rm <path>                Remove VFS file')
        print('  exit                     Exit shell')
