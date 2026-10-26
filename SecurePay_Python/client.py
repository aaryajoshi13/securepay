import json
import socket

DEFAULT_HOST = "127.0.0.1"
PORT = 5050

def send_json(sock, payload):
    sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))

def receive_json(reader):
    line = reader.readline()
    if not line:
        raise ConnectionError("Server closed the connection.")
    return json.loads(line)

def main():
    host = input(f"Server IP [{DEFAULT_HOST}]: ").strip() or DEFAULT_HOST
    username = input("Username: ").strip()
    password = input("Password: ")

    try:
        with socket.create_connection((host, PORT), timeout=10) as sock:
            reader = sock.makefile("r", encoding="utf-8")
            print(receive_json(reader)["message"])
            send_json(sock, {"action": "LOGIN", "username": username, "password": password})
            result = receive_json(reader)
            print(result["message"])
            if not result.get("ok"):
                return
            print(f"Your role: {result['role']}")
            print("Actions: APP_STATUS, FINANCE_REPORT, ADMIN_STATUS, QUIT")
            while True:
                action = input("SecurePay> ").strip().upper()
                if not action:
                    continue
                send_json(sock, {"action": action})
                reply = receive_json(reader)
                print(reply["message"])
                if action == "QUIT":
                    break
    except (OSError, ConnectionError, json.JSONDecodeError) as exc:
        print(f"Could not complete connection: {exc}")

if __name__ == "__main__":
    main()
