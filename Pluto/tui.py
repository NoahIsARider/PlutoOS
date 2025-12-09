"""
Simple curses-based TUI for Pluto userland.
Shows service status and VFS entries, refreshes periodically.
"""
import curses
import time
from Pluto.supervisor import Supervisor
from Pluto.vfs import VFS


def draw(stdscr, sup: Supervisor, vfs: VFS):
    curses.curs_set(0)
    stdscr.nodelay(True)
    while True:
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        stdscr.addstr(0, 2, 'Pluto TUI — Services & VFS (press q to quit)')

        # services
        stdscr.addstr(2, 2, 'Services:')
        status = sup.status()
        row = 3
        for name, info in status.items():
            running = info.get('running')
            pid = info.get('pid')
            line = f" - {name} | running={running} pid={pid}"
            stdscr.addstr(row, 4, line[:w-8])
            row += 1
            # show last log line if present
            logs = info.get('logs_tail', [])
            if logs:
                stdscr.addstr(row, 6, f"last: {logs[-1][:w-12]}")
                row += 1

        # vfs
        row += 1
        stdscr.addstr(row, 2, 'VFS:')
        row += 1
        try:
            files = vfs.ls()
            for f in files:
                stdscr.addstr(row, 4, f[:w-8])
                row += 1
                if row >= h - 2:
                    break
        except Exception as e:
            stdscr.addstr(row, 4, f"(vfs err) {e}")
            row += 1

        stdscr.refresh()
        ch = stdscr.getch()
        if ch == ord('q'):
            break
        time.sleep(0.5)


def run(sup: Supervisor, vfs: VFS):
    curses.wrapper(draw, sup, vfs)


if __name__ == '__main__':
    sup = Supervisor()
    vfs = VFS()
    run(sup, vfs)
