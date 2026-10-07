import os

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("PROXMOX_URL")
userid = os.getenv("PROXMOX_TOKEN")
headers = {"Authorization": userid}



st.set_page_config(page_title="Proxmox Monitor", layout="wide")
st.title("Proxmox Cluster Live Monitor")

def get_node_status(node_num, response, data):
    try:
        if response.status_code != 200:
            return "offline"
        for node in data:
            if (node.get("node") == node_num):
                return node.get("status", "unknown")
    except Exception as e:  # noqa: BLE001
        print(f"Error fetching status for {node_num}: {e}")
        return "offline"
    return "offline"

def get_node_uptime(node_num, response, data):
    try:
        if response.status_code != 200:
            return "unable to fetch"

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

def get_node_telemetry(node_num, node_status_response, nodes_data):
    if(get_node_status(node_num, node_status_response, nodes_data) == 'online'):
        response = requests.get(f"{base_url}/nodes/{node_num}/status", verify = False, headers = headers, timeout = 5)
        if response.status_code != 200:
            return "unable to fetch"
        try:
            return response.json()
        except Exception:  # noqa: BLE001
            return response.text
    return 'Node is either offline or we failed to recieve status'

def get_containers(node_num, node_status_response, nodes_data):
    if (get_node_status(node_num, node_status_response, nodes_data) == "online"):
        response = requests.get(f"{base_url}/nodes/{node_num}/lxc")
        if (response.status_code != 200):
            return "unable to fetch"
        try:
            return response.json()["data"]
        except Exception as e:  # noqa: BLE001
            print(f"Error fetching containers and their status for {node_num}: {e}")
        return "Status code: " + response.status_code

@st.fragment(run_every="1s")
def display_telemetry():
    nodes_response = requests.get(f"{base_url}/nodes", verify = False, headers = headers)
    nodes_data = nodes_response.json().get("data")
    num_of_nodes = len(nodes_data)
    node_names = []
    for i in range(num_of_nodes):
        node_names.append(nodes_data[i].get("node"))

    nodes = []
    for i in range(num_of_nodes):
        nodes.append(get_node_telemetry(node_names[i], nodes_response, nodes_data)["data"])

    node_uptimes = []
    for i in range(num_of_nodes):
        node_uptimes.append(get_node_uptime(node_names[i], nodes_response, nodes_data))

    node_cpu_usages = []
    for i in range(num_of_nodes):
        cpu_unclamped = nodes[i].get("cpu")
        node_cpu_usages.append(min(max(float(cpu_unclamped), 0.0), 1.0))

    node_mem_usages = []
    for i in range(num_of_nodes):
        mem_dict = nodes[i].get("memory")
        mem_usage = mem_dict.get("available")
        mem_total = mem_dict.get("total")
        node_mem_usages.append(min(max(float((mem_total - mem_usage) / mem_total), 0.0), 1.0))

    for i in range(num_of_nodes):
        st.progress(value = node_cpu_usages[i], text = f"{node_names[i]} CPU's usage: {node_cpu_usages[i] * 100}%")

    for i in range(num_of_nodes):
        st.progress(value = node_mem_usages[i], text = f"{node_names[i]} RAM's usage: {node_mem_usages[i] * 100}%")

    for i in range(num_of_nodes):
        st.caption(body = node_uptimes[i])

display_telemetry()
