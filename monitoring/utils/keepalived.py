import ipaddress, os, sys
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
# Aggiungi la directory parent al path
sys.path.insert(0, parent_dir)

from config import this_machine_ip

def calculate_priority(ip, base=100):
    return base + int(ipaddress.IPv4Address(ip)) % 900

def generate_keepalived_config():
    interface = "eth0"  # Sostituiscilo con l'interfaccia corretta, o rilevala dinamicamente
    priority = calculate_priority(this_machine_ip)
    password = "m@st3rP@ssw0rd$"

    config = f"""
vrrp_script chk_main_py {{
    script "pgrep -f main.py"
    interval 5
    timeout 3
    fall 2
    rise 1
}}

vrrp_script chk_api_server {{
    script "pgrep -f api_server.py"
    interval 5
    timeout 3
    fall 2
    rise 1
}}

vrrp_instance VI_1 {{
    state BACKUP
    interface {interface}
    virtual_router_id 162
    priority {priority}
    advert_int 1
    authentication {{
        auth_type PASS
        auth_pass {password}
    }}
    log_file /var/log/keepalived.log
    log_level 7
    virtual_ipaddress {{
        203.0.113.1
    }}
    track_script {{
        chk_main_py
        chk_api_server
    }}
}}
"""
    # # Scrivi il file
    keepalived_conf_path = '/etc/keepalived/keepalived.conf'  # Cambialo se vuoi salvarlo altrove
    with open(keepalived_conf_path, 'w') as f:
        f.write(config)

    print(f"Configurazione keepalived generata con priorità {priority} per IP {this_machine_ip}")

# Esegui la funzione solo se chiamato direttamente
if __name__ == "__main__":
    generate_keepalived_config()
