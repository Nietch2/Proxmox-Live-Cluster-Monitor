import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("PROXMOX_URL")
userid = os.getenv("PROXMOX_TOKEN")
node_num = os.getenv("NODE1")
node_num2 = os.getenv("NODE2")
headers = {"Authorization": userid}

st.set_page_config(page_title="Proxmox Monitor", layout="wide")
st.title("Proxmox Cluster Live Monitor")

def get_node_status(node_num):
    try:
        response = requests.get(f"{base_url}/nodes", verify = False, headers = headers)
        if response.status_code != 200:
            return "offline"
        data = response.json().get("data")
        for node in data:
            if (node.get("node") == node_num):
                return node.get("status", "unknown")
    except Exception as e:  # noqa: BLE001
        print(f"Error fetching status for {node_num}: {e}")
        return "offline"
    return "offline"

def get_node_uptime(node_num):
    try:
        response = requests.get(f"{base_url}/nodes", verify = False, headers = headers)
        if response.status_code != 200:
            return "unable to fetch"
        data = response.json().get("data")
        for node in data:
            if (node.get("node") == node_num):
                node_uptime = node.get("uptime", "unknown")

        weeks = 0
        days = 0
        hours = 0
        minutes = 0
        if (node_uptime // 604800> 0):
            weeks += node_uptime // 604800
            node_uptime -= weeks * 604800
        if (node_uptime // 86400 > 0):
            days += node_uptime // 86400
            node_uptime -= days * 86400
        if (node_uptime // 3600 > 0):
            hours += node_uptime // 3600
            node_uptime -= hours * 3600
        if (node_uptime // 60 > 0):
            minutes += node_uptime // 60
            node_uptime -= minutes * 60
        return (f"Weeks: {weeks}, Days: {days}, Hours: {hours}, Minutes: {minutes}, Seconds: {node_uptime}")
    except Exception as e:  # noqa: BLE001
        print(f"Error fetching uptime for {node_num}: {e}")
    return response.status_code

def get_node_telemetry(node_num):
    if(get_node_status(node_num) == 'online'):
        response = requests.get(f"{base_url}/nodes/{node_num}/status", verify = False, headers = headers, timeout = 5)
        if response.status_code != 200:
            return "unable to fetch"
        try:
            return response.json()
        except Exception:  # noqa: BLE001
            return response.text
    return 'Node is either offline or we failed to recieve status'

def get_containers(node_num):
    if (get_node_status(node_num) == "online"):
        response = requests.get(f"{base_url}/nodes/{node_num}/lxc")

@st.fragment(run_every="1s")
def display_telemetry():
    node_info = get_node_telemetry(node_num)
    node_info2 = get_node_telemetry(node_num2)
    node = node_info["data"]
    node2 = node_info2["data"]

    node_uptime = get_node_uptime(node_num)
    node_uptime2 = get_node_uptime(node_num2)

    cpu_usage = node.get("cpu")
    cpu_usage2 = node2.get("cpu")
    cpu1_clamped = min(max(float(cpu_usage), 0.0), 1.0)
    cpu2_clamped = min(max(float(cpu_usage2), 0.0), 1.0)

    mem_dict = node.get("memory")
    mem_dict2 = node2.get("memory")
    mem_usage = mem_dict.get("available")
    mem_usage2 = mem_dict2.get("available")
    mem_total = mem_dict.get("total")
    mem_total2 = mem_dict2.get("total")
    mem1_clamped = min(max(float((mem_total - mem_usage) / mem_total), 0.0), 1.0)
    mem2_clamped = min(max(float((mem_total2 - mem_usage2) / mem_total2), 0.0), 1.0)
    
    st.progress(value = cpu1_clamped, text = f"{node_num} CPU's usage: {cpu1_clamped * 100}%")
    st.progress(value = cpu2_clamped, text = f"{node_num2} CPU's usage: {cpu2_clamped * 100}%")

    st.progress(value = mem1_clamped, text = f"{node_num} RAM's usage: {mem1_clamped * 100}%")
    st.progress(value = mem2_clamped, text = f"{node_num2} RAM's usage: {mem2_clamped * 100}%")

    st.caption(body = node_uptime)
    st.caption(body = node_uptime2)
display_telemetry()
