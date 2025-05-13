import subprocess
import socket

def check_process(name):
    """Sprawdza, czy proces o danej nazwie działa"""
    try:
        result = subprocess.run(["pgrep", "-f", name], stdout=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def check_port(port):
    """Sprawdza, czy port TCP jest otwarty (czy działa serwer)"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        result = sock.connect_ex(("127.0.0.1", port))
        return result == 0

def main():
    print("🔎 Sprawdzanie statusu systemu...\n")

    print(f"Scraper (main.py): {'✅ działa' if check_process('main.py') else '❌ nie działa'}")
    print(f"Cron: {'✅ działa' if check_process('cron') else '❌ nie działa'}")
    print(f"Backend: {'✅ działa' if check_port(5555) else '❌ nie działa'}")
    print(f"Frontend:")
    print(f"  - Port {80}: {'✅ otwarty' if check_port(80) else '❌ zamknięty'}")

if __name__ == "__main__":
    main()
