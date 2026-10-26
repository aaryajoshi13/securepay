import json
import logging
import socket
import threading
from pathlib import Path

import requests

from authentication import authenticate
from access_control import is_allowed

HOST = "0.0.0.0"
PORT = 5050
BUFFER_SIZE = 4096
BASE_DIR = Path(__file__).resolve().parent

CONTROLLER_URL = "http://localhost:58000/api/v1"

APP_SERVER_IP = "192.168.50.10"

logging.basicConfig(
    filename=BASE_DIR / "securepay_activity.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


def get_controller_ticket(username, password):
    response = requests.post(
        f"{CONTROLLER_URL}/ticket",
        json={
            "username": username,
            "password": password
        },
        timeout=10
    )

    response.raise_for_status()

    ticket = response.json().get("response", {}).get("serviceTicket")

    if not ticket:
        raise RuntimeError("Packet Tracer authentication failed.")

    return ticket


def controller_get(endpoint, ticket):
    response = requests.get(
        f"{CONTROLLER_URL}/{endpoint}",
        headers={"X-Auth-Token": ticket},
        timeout=10
    )

    response.raise_for_status()

    return response.json().get("response", [])


def get_packet_tracer_hosts(ticket):
    return controller_get("host", ticket)


def get_packet_tracer_devices(ticket):
    return controller_get("network-device", ticket)


def check_network(hosts, devices):
    print("\n" + "=" * 60)
    print("       SECUREPAY NETWORK STATUS")
    print("=" * 60)

    managed_devices = [
        device for device in devices
        if device.get("collectionStatus") == "Managed"
    ]

    reachable_devices = [
        device for device in managed_devices
        if device.get("reachabilityStatus") == "Reachable"
    ]

    successful_hosts = [
        host for host in hosts
        if host.get("pingStatus") == "SUCCESS"
    ]

    print(f"Managed devices: {len(managed_devices)}")
    print(f"Reachable devices: {len(reachable_devices)}")
    print(f"Discovered hosts: {len(hosts)}")
    print(f"Successful host pings: {len(successful_hosts)}")

    app_host = next(
        (
            host for host in hosts
            if host.get("hostIp") == APP_SERVER_IP
        ),
        None
    )

    if app_host:
        app_status = app_host.get("pingStatus", "UNKNOWN")
        print(f"\nSecurePay App Server: {APP_SERVER_IP}")
        print(f"Controller ping status: {app_status}")
    else:
        app_status = "NOT_DISCOVERED"
        print(f"\nSecurePay App Server: {APP_SERVER_IP}")
        print("Controller ping status: NOT DISCOVERED")

    print("=" * 60)

    logging.info(
        "NETWORK_CHECK managed=%s reachable=%s hosts=%s successful=%s app_server=%s",
        len(managed_devices),
        len(reachable_devices),
        len(hosts),
        len(successful_hosts),
        app_status
    )

    return app_status == "SUCCESS"



def send_json(conn, payload):
    conn.sendall(
        (json.dumps(payload) + "\n").encode("utf-8")
    )


def receive_json(reader):
    line = reader.readline()

    if not line:
        return None

    return json.loads(line)


def handle_client(conn, address):
    peer = f"{address[0]}:{address[1]}"

    logging.info("CONNECT peer=%s", peer)

    username = None

    try:
        conn.settimeout(60)

        reader = conn.makefile(
            "r",
            encoding="utf-8"
        )

        send_json(conn, {
            "ok": True,
            "message": "Welcome to SecurePay demo. Authenticate to continue.",
            "actions": [
                "APP_STATUS",
                "FINANCE_REPORT",
                "ADMIN_STATUS",
                "QUIT"
            ]
        })

        request = receive_json(reader)

        if not request or request.get("action") != "LOGIN":
            logging.warning(
                "AUTH_REJECT peer=%s reason=login_required",
                peer
            )

            send_json(conn, {
                "ok": False,
                "message": "Login required."
            })

            return

        username = str(request.get("username", ""))[:80]
        password = str(request.get("password", ""))

        user = authenticate(username, password)

        if not user:
            logging.warning(
                "AUTH_FAIL username=%s peer=%s",
                username,
                peer
            )

            send_json(conn, {
                "ok": False,
                "message": "Authentication failed."
            })

            return

        role = user["role"]

        logging.info(
            "AUTH_SUCCESS username=%s role=%s peer=%s",
            username,
            role,
            peer
        )

        send_json(conn, {
            "ok": True,
            "message": "Authenticated.",
            "role": role
        })

        while True:
            request = receive_json(reader)

            if request is None:
                break

            action = str(
                request.get("action", "")
            ).upper()

            if action == "QUIT":
                send_json(conn, {
                    "ok": True,
                    "message": "Goodbye."
                })

                break

            if not is_allowed(role, action):
                logging.warning(
                    "ACCESS_DENIED username=%s role=%s action=%s peer=%s",
                    username,
                    role,
                    action,
                    peer
                )

                send_json(conn, {
                    "ok": False,
                    "message": "Access denied for this role."
                })

                continue

            logging.info(
                "ACCESS_GRANTED username=%s role=%s action=%s peer=%s",
                username,
                role,
                action,
                peer
            )

            responses = {
                "APP_STATUS":
                    "SecurePay application server is online.",

                "FINANCE_REPORT":
                    "Demo finance report: transaction_count=0; status=SIMULATED.",

                "ADMIN_STATUS":
                    "Administrative status: network security demo is running."
            }

            send_json(conn, {
                "ok": True,
                "message": responses.get(
                    action,
                    "Action completed."
                )
            })

    except (json.JSONDecodeError, UnicodeDecodeError):
        logging.warning("BAD_REQUEST peer=%s", peer)

        try:
            send_json(conn, {
                "ok": False,
                "message": "Malformed request."
            })

        except OSError:
            pass

    except (ConnectionError, OSError, socket.timeout) as exc:
        logging.info(
            "CONNECTION_END peer=%s detail=%s",
            peer,
            type(exc).__name__
        )

    finally:
        try:
            conn.close()

        finally:
            logging.info(
                "DISCONNECT username=%s peer=%s",
                username or "-",
                peer
            )


def main():
    print("SecurePay - Packet Tracer Integrated Server")

    username = input("Controller username: ").strip()
    password = input("Controller password: ")

    try:
        ticket = get_controller_ticket(
            username,
            password
        )

        print("\nController authentication successful.")

        hosts = get_packet_tracer_hosts(ticket)
        devices = get_packet_tracer_devices(ticket)

        network_ready = check_network(
            hosts,
            devices
        )

        if not network_ready:
            print(
                "\nSecurePay server startup cancelled: "
                "the application server is not reporting SUCCESS."
            )

            logging.error(
                "SERVER_START_CANCELLED reason=app_server_not_successful"
            )

            return

    except requests.RequestException as exc:
        print(f"\nController API error: {exc}")

        logging.error(
            "CONTROLLER_API_ERROR detail=%s",
            type(exc).__name__
        )

        return

    except RuntimeError as exc:
        print(f"\nIntegration error: {exc}")

        logging.error(
            "INTEGRATION_ERROR detail=%s",
            str(exc)
        )

        return

    print("\nNetwork check successful.")
    print(f"SecurePay TCP server listening on {HOST}:{PORT}")

    logging.info("SERVER_START host=%s port=%s", HOST, PORT)

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server:

        server.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server.bind((HOST, PORT))
        server.listen(10)

        while True:
            conn, address = server.accept()

            thread = threading.Thread(
                target=handle_client,
                args=(conn, address),
                daemon=True
            )

            thread.start()


if __name__ == "__main__":
    main()