import json, os, sys, re, asyncio

# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
# Aggiungi la directory parent al path
sys.path.insert(0, parent_dir)
# Entra nel adirectory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Entra nel adirectory mon
bot_dir = os.path.join(parent_dir, 'bot_Discord')
from bot_Discord import bot
# Aggiungi la directory mon al path
sys.path.insert(0, mon_dir)
# Costruisci il percorso del file hosts.json nella cartella 'mon'
hosts_path = os.path.join(mon_dir, 'hosts.json')

def verify_ip(ip = None):
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if re.match(pattern, ip):
        ottetti = ip.split(".")
        if all(0 <= int(octeto) <= 255 for octeto in ottetti ):
            print("Ip address valid.")
            return True
        else:
            print("Ip address not valid, out of range.")
            return False
    else:
        print("Ip address not valid.")
        return False

def add_device():
    with open(hosts_path, 'r') as file:
        data = json.load(file)
    hosts = data.get('hosts', {})
    forgot = data.get('forgot', {})
    this_device_ip = data.get('this_device_ip', {})
    to_monitor = data.get('to_monitor', {})

    to_check_keys = set(hosts.keys()) | set(forgot.keys()) | set(this_device_ip.keys()) | set(to_monitor.keys())
    to_check_ip = set(hosts.values()) | set(forgot.values()) | set(this_device_ip.values()) | set(to_monitor.values())

    hostname = input("Inserisci il hostname: ")
    while not hostname or hostname in to_check_keys:
        if not hostname:
            print("Hostname non può essere vuoto.")
        else:
            print(f"Hostname '{hostname}' già esistente o da eliminare.")
        hostname = input("Inserisci un nuovo hostname: ")

    ip = input("Inserisci l'indirizzo IP: ")
    while not verify_ip(ip):
        ip = input("Inserisci un nuovo indirizzo IP: ")
    while not ip or ip in to_check_ip:
        if not ip:
            print("IP non può essere vuoto.")
        else:
            print(f"l'ip '{ip}' già esistente o da eliminare.")
        ip = input("Inserisci un nuovo ip: ")

    print(f"Dispositivo {hostname} con IP {ip} aggiunto.")
    to_monitor[hostname] = ip
    data['to_monitor'] = to_monitor
    with open(hosts_path, 'w') as file:
        json.dump(data, file, indent=4)

add_device()