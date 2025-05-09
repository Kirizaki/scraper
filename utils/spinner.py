import sys
import threading
import itertools
import time

class Spinner:
    def __init__(self, message="🔄 Pracuję..."):
        self.spinner = itertools.cycle(['|', '/', '-', '\\'])
        self.running = False
        self.thread = None
        self.message = message

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def _spin(self):
        while self.running:
            sys.stdout.write(f"\r{self.message} {next(self.spinner)}")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        sys.stdout.write("\r✅ Gotowe!                    \n")
        sys.stdout.flush()
