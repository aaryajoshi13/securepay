# SecurePay Python Client–Server Security Demo

This coursework prototype demonstrates:
1. TCP client–server communication using Python sockets.
2. Authentication using salted PBKDF2 password hashes.
3. Role-based application access control.
4. Activity logging for connections, authentication, and access decisions.

It uses simulated responses only; it does not process real payments or store real financial data.

## Requirements
- Python 3.9+ (no third-party packages required)
- Run on two machines/VMs for a network demonstration, or run both locally for an initial smoke test.

## 1. Create demo users
In this folder, run:
```bash
python3 make_users.py
```
This creates `users.json`. Demo accounts:
- `hr_demo` / `HRdemo!234`
- `finance_demo` / `FinanceDemo!234`
- `itadmin_demo` / `ITadminDemo!234`
- `support_demo` / `SupportDemo!234`
- `guest_demo` / `GuestDemo!234`

These credentials are for a local coursework demo only.

## 2. Start the server
On the server machine:
```bash
python3 server.py
```
The server listens on TCP port 5050 on all network interfaces.

## 3. Start a client
On the client machine:
```bash
python3 client.py
```
Enter the server machine's reachable IP address. For a local smoke test, use `127.0.0.1`.

## 4. Demonstrate RBAC
Login as each role and try:
- `APP_STATUS`: all roles should be allowed.
- `FINANCE_REPORT`: only FINANCE and IT_ADMIN should be allowed.
- `ADMIN_STATUS`: only IT_ADMIN should be allowed.
- `QUIT`: closes the session.

## 5. View activity log
The server writes `securepay_activity.log` beside `server.py`. It records connection events, login success/failure, and granted/denied actions. Passwords are never logged.

## Network integration note
Packet Tracer PCs/servers do not execute arbitrary Python socket code. To demonstrate traffic passing through the Cisco topology, run the Python client and server on real hosts or VMs connected to the actual routed network. They must have IP reachability through the router/switch path and permitted TCP/5050 traffic. Merely running both programs on one Mac proves socket functionality, not traversal through the Packet Tracer topology. Do not claim Packet Tracer integration until the hosts are genuinely connected to that network.



# SECUREPAY NETWORK CONFIGURATION & VERIFICATION

1. VLAN CONFIGURATION
Location: Switch S1/S2 CLI

VLANs:
10 - HR
20 - Finance
30 - IT Admin
40 - Support
50 - Servers
60 - Guest
99 - Management

Verify:
show vlan brief
show interfaces trunk

2. INTER-VLAN ROUTING
Location: Router R1 CLI

Router subinterfaces:
G0/0/0.10 - 192.168.10.1
G0/0/0.20 - 192.168.20.1
G0/0/0.30 - 192.168.30.1
G0/0/0.40 - 192.168.40.1
G0/0/0.50 - 192.168.50.1
G0/0/0.60 - 192.168.60.1
G0/0/0.99 - 192.168.99.1

Verify:
show ip interface brief
show ip interface

3. ACCESS CONTROL LISTS (ACL)
Location: Router R1 CLI

ACLs:
HR_RESTRICTIONS - VLAN 10
FINANCE_RESTRICTIONS - VLAN 20
SUPPORT_RESTRICTIONS - VLAN 40
GUEST_RESTRICTIONS - VLAN 60

Verify:
show access-lists
show ip interface
show running-config

4. PORT SECURITY
Location: Switch S1 CLI

Protected ports:
Fa0/1 - HR
Fa0/2 - Finance
Fa0/3 - IT Admin

Features:
Maximum 1 MAC address
Sticky MAC learning
Violation action: Shutdown

Verify:
show port-security
show port-security interface fa0/1
show port-security interface fa0/2
show port-security interface fa0/3
show interfaces status

5. DHCP
Location: Router R1 CLI

DHCP pools configured for departmental VLANs.

Verify:
show ip dhcp pool
show ip dhcp binding
show ip dhcp excluded-address

6. DHCP SNOOPING
Location: Switch S1 CLI

Enabled VLANs: 10, 20, 30, 40, 50, 60
Trusted ports: G0/1, G0/2
Untrusted ports: Fa0/1, Fa0/2, Fa0/3
Option 82: Disabled

Verify:
show ip dhcp snooping
show ip dhcp snooping binding

7. SAVE CONFIGURATION
Location: Router and Switch CLI

copy running-config startup-config

8. FINAL

Router:
show ip interface brief
show ip interface
show access-lists
show ip dhcp pool
show ip dhcp binding

Switch:
show vlan brief
show interfaces trunk
show port-security
show ip dhcp snooping
show running-config
