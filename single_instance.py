import socket
import sys
import threading

PORT = 49281  # Dedicated localhost port for Desktop Cat Voice Listener lock

class SingleInstanceManager:
    """Enforces single-instance execution and wakes up the running instance on subsequent launches."""
    
    def __init__(self, on_activate=None):
        self.on_activate = on_activate
        self._server = None
        self._running = False

    def acquire_lock_or_wake_existing(self):
        """
        Attempts to acquire the single-instance lock.
        If another instance is already running, sends a 'SHOW' signal to it and exits.
        """
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self._server.bind(("127.0.0.1", PORT))
            self._server.listen(2)
            self._running = True
            
            # Start background listener thread for subsequent launches
            t = threading.Thread(target=self._listen_loop, daemon=True)
            t.start()
            return True
        except OSError:
            # Another instance is already active
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.settimeout(2.0)
                client.connect(("127.0.0.1", PORT))
                client.sendall(b"SHOW")
                client.close()
            except Exception as e:
                print(f"[SingleInstance] Signal to existing instance failed: {e}")
                
            print("[SingleInstance] Another instance is already running. Signaled existing instance and exiting.")
            sys.exit(0)

    def _listen_loop(self):
        while self._running:
            try:
                conn, _ = self._server.accept()
                msg = conn.recv(1024).decode("utf-8", errors="ignore").strip()
                if msg == "SHOW" and self.on_activate:
                    self.on_activate()
                conn.close()
            except Exception:
                break

    def release(self):
        self._running = False
        if self._server:
            try:
                self._server.close()
            except Exception:
                pass
