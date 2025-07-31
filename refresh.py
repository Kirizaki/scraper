import subprocess
import time
import os
import shutil
import socket
from datetime import datetime
import signal
import psutil

WSGI_PORT = 5555
WSGI_FILE = "wsgi.py"
WYNIKI_FILE = "wyniki.csv"
MAIN_SCRIPT = "main.py"


def is_port_in_use(port):
    """Check if a given port is being used (server running)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


def kill_process_on_port(port):
    """Kill the process using the specified port."""
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        try:
            for conn in proc.connections(kind='inet'):
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} on port {port}")
                    proc.send_signal(signal.SIGTERM)
                    proc.wait(timeout=5)
                    return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue


def backup_file(file_path):
    """Backup the file by copying with a timestamp."""
    if not os.path.exists(file_path):
        print(f"{file_path} does not exist. Skipping backup.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file_path)
    backup_name = f"{timestamp}_{os.path.basename(file_path)}"
    shutil.copy(file_path, backup_name)
    print(f"Backed up {file_path} to {backup_name}")


def start_wsgi():
    """Start the WSGI server."""
    print("Starting WSGI server...")
    return subprocess.Popen(["python3", WSGI_FILE])


def run_main():
    """Run the main.py script."""
    print("Running main.py...")
    subprocess.run(["python3", MAIN_SCRIPT])


if __name__ == "__main__":
    # Restart or start the WSGI server
    if is_port_in_use(WSGI_PORT):
        print(f"Port {WSGI_PORT} is in use. Restarting server...")
        kill_process_on_port(WSGI_PORT)
        time.sleep(1)

    wsgi_process = start_wsgi()
    time.sleep(2)  # Wait a bit for the server to be up

    # Backup wyniki.csv
    backup_file(WYNIKI_FILE)

    # Run main.py
    run_main()

    # Optional: keep the server alive, or terminate after main
    print("Controller script finished.")
