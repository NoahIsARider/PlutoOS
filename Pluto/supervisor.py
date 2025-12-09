"""
Simple Supervisor: launch/monitor/restart services (userland service manager).
"""
import subprocess
import threading
import time
import sys
from typing import Dict


class Service:
    def __init__(self, name: str, cmd, restart: bool = True):
        self.name = name
        self.cmd = cmd
        self.restart = restart
        self.process = None
        self._monitor_thread = None
        self._stop = threading.Event()
        self._log_lines = []
        self._log_lock = threading.Lock()

    def start(self):
        if self.process and self.process.poll() is None:
            return
        self._stop.clear()
        # capture stdout/stderr for logs
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        # start a thread to read process output
        threading.Thread(target=self._read_output, daemon=True).start()
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _read_output(self):
        if not self.process or not self.process.stdout:
            return
        for line in self.process.stdout:
            with self._log_lock:
                self._log_lines.append(line.rstrip('\n'))
                # keep last N lines
                if len(self._log_lines) > 1000:
                    self._log_lines.pop(0)

    def _monitor(self):
        while not self._stop.is_set():
            if self.process is None:
                break
            rc = self.process.poll()
            if rc is not None:
                # process exited
                if self.restart:
                    time.sleep(0.5)
                    self.start()
                else:
                    break
            time.sleep(0.5)

    def stop(self):
        self._stop.set()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass
        self.process = None

    def get_logs(self, tail: int = 50):
        with self._log_lock:
            return list(self._log_lines[-tail:])


class Supervisor:
    def __init__(self):
        self.services: Dict[str, Service] = {}
        self.lock = threading.Lock()

    def register_service(self, name: str, cmd, restart: bool = True):
        with self.lock:
            svc = Service(name, cmd, restart=restart)
            self.services[name] = svc

    def start_service(self, name: str):
        with self.lock:
            svc = self.services.get(name)
            if not svc:
                raise KeyError(name)
            svc.start()

    def stop_service(self, name: str):
        with self.lock:
            svc = self.services.get(name)
            if not svc:
                return
            svc.stop()

    def start_all(self):
        with self.lock:
            for svc in list(self.services.values()):
                svc.start()

    def stop_all(self):
        with self.lock:
            for svc in list(self.services.values()):
                svc.stop()

    def status(self):
        out = {}
        with self.lock:
            for name, svc in self.services.items():
                running = (svc.process is not None and svc.process.poll() is None)
                out[name] = {'running': running, 'pid': getattr(svc.process, 'pid', None), 'logs_tail': svc.get_logs(10)}
        return out
