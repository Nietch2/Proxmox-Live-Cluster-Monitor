# Proxmox Live Cluster Monitor

A lightweight, real-time Proxmox VE cluster telemetry dashboard built with Python and Streamlit. This application polls the Proxmox REST API to display live hardware utilization metrics across cluster nodes with automatic background refreshes.

---

## Features

* **Live Telemetry:** Tracks CPU utilization and memory consumption side by side for cluster nodes.
* **Accurate Memory Accounting:** Uses Linux kernel `available` memory rather than basic `free` counters to correctly account for reclaimable disk caches.


* **Uptime Tracking:** Parses raw host uptime seconds into standard, human-readable units (weeks, days, hours, minutes, seconds).
* **Auto-Refreshing UI:** Employs Streamlit fragments (`@st.fragment`) to update hardware metrics at a consistent interval without full browser refreshes.
* **Secure Configuration:** Zero hardcoded credentials or IP addresses; all environment variables are parsed through Python `.env` management.

---

## Architecture & API Telemetry

The dashboard communicates directly with the Proxmox VE API (`/api2/json`):

* **`/nodes`**: Queries cluster membership, current online/offline status, and broadcast uptime metrics.


* **`/nodes/{node}/status`**: Extracts live host hardware metrics, including direct CPU ratios and memory allocation tables.



---

## Prerequisites

* **Python 3.10+**
* **Proxmox VE 7.x / 8.x** cluster
* A Proxmox API token with sufficient read permissions (e.g., `PVEAuditor` role assigned to `/` or the target nodes)

> **Important:** Ensure the API Token is created with **Privilege Separation disabled** (or that explicit permissions are mapped to the Token ID), otherwise calls to `/nodes/{node}/status` will return `403 Forbidden`.

---

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Nietch2/Proxmox-Live-Cluster-Monitor.git
cd <your-repo-name>

```


2. **Create and activate a virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install streamlit requests python-dotenv urllib3

```



---

## Configuration

Create a `.env` file in the root directory:

```env
PROXMOX_URL=https://<proxmox-host-or-ip>:8006/api2/json
PROXMOX_TOKEN=PVEAPIToken=root@pam!monitoring=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
NODE1=pve1
NODE2=pve2

```

### Environment Variable Reference

| Variable | Description | Example |
| --- | --- | --- |
| `PROXMOX_URL` | Base API endpoint of any online cluster node | `[https://192.168.1.100:8006/api2/json](https://192.168.1.100:8006/api2/json)` |
| `PROXMOX_TOKEN` | Full Proxmox API Token header value | `PVEAPIToken=user@realm!tokenid=uuid` |
| `NODE1` | Exact hostname of your first cluster node | `pve` |
| `NODE2` | Exact hostname of your second cluster node | `pve-backup` |

---

## Running the Dashboard

Launch the application using Streamlit:

```bash
streamlit run ProxmoxDashboard.py

```

The dashboard will open automatically in your browser at `http://localhost:8501`.

---

## Security Notes

* Self-signed TLS certificate warnings from Proxmox are suppressed locally via `urllib3.disable_warnings`.
* Never commit your `.env` file. Ensure `.env` is listed inside your `.gitignore` prior to pushing to remote git repositories.

---

## Planned Enhancements

* Dynamic multi-node discovery (removing static node names from `.env`).


* Granular storage pool / ZFS dataset allocation metrics.
* Running VM and LXC container tables per host.
* Host load average and I/O wait monitoring.