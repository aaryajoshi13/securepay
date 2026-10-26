import requests

CONTROLLER_URL = "http://localhost:58000/api/v1"


def get_ticket(username, password):
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


def api_get(endpoint, ticket):
    response = requests.get(
        f"{CONTROLLER_URL}/{endpoint}",
        headers={"X-Auth-Token": ticket},
        timeout=10
    )

    response.raise_for_status()
    return response.json().get("response", [])


def get_hosts(ticket):
    return api_get("host", ticket)


def get_network_devices(ticket):
    return api_get("network-device", ticket)


def display_report(hosts, devices):
    print("\n" + "=" * 65)
    print("       SECUREPAY NETWORK STATUS REPORT")
    print("=" * 65)

    print("\nNETWORK DEVICES")
    print("-" * 65)

    managed_count = 0

    for device in devices:
        hostname = device.get("hostname", "Unknown")
        device_type = device.get("type", "Unknown")
        ip = device.get("managementIpAddress", "N/A")
        collection = device.get("collectionStatus", "Unknown")
        reachability = device.get("reachabilityStatus", "Unknown")

        if collection == "Managed":
            managed_count += 1

        print(f"Device:       {hostname}")
        print(f"Type:         {device_type}")
        print(f"Management IP:{ip}")
        print(f"Management:   {collection}")
        print(f"Reachability: {reachability}")
        print("-" * 65)

    print("\nEND DEVICES")
    print("-" * 65)

    successful_hosts = 0

    for host in hosts:
        name = host.get("hostName", "Unknown")
        ip = host.get("hostIp", "N/A")
        host_type = host.get("hostType", "Unknown")
        switch = host.get("connectedNetworkDeviceIpAddress", "N/A")
        port = host.get("connectedInterfaceName", "N/A")
        ping = host.get("pingStatus", "Unknown")

        if ping == "SUCCESS":
            successful_hosts += 1

        print(
            f"{name:<15} "
            f"{ip:<18} "
            f"{host_type:<10} "
            f"{ping}"
        )

        print(f"  Connected switch: {switch}")
        print(f"  Switch port:      {port}")

    print("\n" + "=" * 65)
    print("SUMMARY")
    print("-" * 65)
    print(f"Managed network devices: {managed_count}")
    print(f"Total discovered hosts:  {len(hosts)}")
    print(f"Hosts reporting SUCCESS: {successful_hosts}")
    print("=" * 65)


def main():
    print("SecurePay - Packet Tracer Network Integration")

    username = input("Controller username: ").strip()
    password = input("Controller password: ")

    try:
        ticket = get_ticket(username, password)

        print("\nController authentication successful.")

        hosts = get_hosts(ticket)
        devices = get_network_devices(ticket)

        display_report(hosts, devices)

    except requests.RequestException as exc:
        print(f"\nAPI connection error: {exc}")

    except (RuntimeError, ValueError) as exc:
        print(f"\nIntegration error: {exc}")


if __name__ == "__main__":
    main()