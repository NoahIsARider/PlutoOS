"""
Simple Kernel for PlutoOS: service registry and event bus.
"""
import threading
import queue

class Kernel:
    def __init__(self, name="PlutoOS"):
        self.name = name
        self.services = {}
        self.event_queue = queue.Queue()
        self._running = False
        self._thread = None

    def register_service(self, name, handler):
        """Register a service handler that accepts one event argument."""
        self.services[name] = handler

    def emit_event(self, event):
        self.event_queue.put(event)

    def _loop(self):
        while self._running:
            try:
                ev = self.event_queue.get(timeout=0.5)
                # dispatch to services
                for svc in list(self.services.values()):
                    try:
                        svc(ev)
                    except Exception:
                        pass
            except Exception:
                pass

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
