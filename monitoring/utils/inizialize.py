import pyotp, subprocess, os, sys
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
# Aggiungi la directory parent al path
sys.path.insert(0, parent_dir)
# Trova la directory ssl
ssl_folder = os.path.join(parent_dir,'server', 'ssl')

# Genera una chiave segreta base32
secret = pyotp.random_base32()
print("Chiave segreta:", secret)

# Crea certificato CA
def command_build(openssl_command):
    result = subprocess.run(
                openssl_command, 
                shell=True, 
                capture_output=True, 
                text=True
            )
    return result

crea_ca_key = f"openssl genrsa -out {ssl_folder}/ca.key 4096"
result =command_build(crea_ca_key)
if result.returncode == 0:
    print("Chiave privata della CA generata con successo.")
    crea_ca_crt = f'openssl req -x509 -new -nodes -key {ssl_folder}/ca.key -sha256 -days 3650 -out {ssl_folder}/ca.crt -subj "/C=IT/ST=Veneto/L=Treviso/O=Pxnjo/CN=Pxnjo Monitoring CA"'
    result =command_build(crea_ca_crt)
    # Verifica se ci sono errori nell'esecuzione
    if result.returncode == 0:
        print("Certificato della CA generata con successo.")
    else:
        print(f"Errore nella creazione del Certificato: {result.stderr}")
else:
    print(f"Errore nella creazione della chiave della CA: {result.stderr}")