import json, os, sys

# Ottieni la directory corrente di setup.py
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
# Entra nel adirectory mon
mon_dir = os.path.join(parent_dir, 'mon')
# Aggiungi la directory mon al path
sys.path.insert(0, mon_dir)
# Aggiungi la directory parent al path
sys.path.insert(0, parent_dir)
# Costruisci il percorso del file hosts.json nella cartella 'mon'
hosts_path = os.path.join(mon_dir, 'hosts.json')

def forgot_device():
    with open(hosts_path, 'r') as f:
        data = json.load(f)
    
    hosts = data.get('hosts', {})
    forgot = data.get('forgot', {})
    to_monitor = data.get('to_monitor', {})

    all_devices = set(hosts.keys()) | set(to_monitor.keys())

    if not all_devices:
        print("Nessun dispositivo presente in 'hosts' o 'to_monitor'.")
        return

    print(f"Current devices: {all_devices}")
    hostname  = input("Enter the hostname of the device you want to remove: ")

    while hostname  not in all_devices:
        print("Hostname not found.")
        hostname  = input("Enter the hostname of the device you want to remove: ")

    # Se esiste, rimuovi l'host dal suo dizionario e spostalo in "forgot"
    if hostname in to_monitor:
        ip = to_monitor.pop(hostname)
    elif hostname in hosts:
        ip = hosts.pop(hostname)
    
    forgot[hostname] = ip

    # Aggiorna i campi nel dizionario originale
    data['hosts'] = hosts
    data['to_monitor'] = to_monitor
    data['forgot'] = forgot

    # Salviamo tutto il dizionario originale con la nuova chiave
    with open(hosts_path, 'w') as f:
        json.dump(data, f, indent=4)

forgot_device()