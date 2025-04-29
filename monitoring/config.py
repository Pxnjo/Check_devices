this_machine_hostname = "" # hostname della macchina corrente
this_machine_ip = "" # ip della macchina corrente
hostname = "" # hostname della prima macchina da monitorare 
ip = "" # ip della prima macchina da monitorare
# new_infrastructure = False # Se è una nuova infrastruttura crea tutto da zero

###################################################################
#__________________________WARNING________________________________#
###################################################################
# NON MODIFICARE QUESTE VARIABILI A MENO CHE NON SIA NECESSARIO

import pyotp

TOTP_KEY = ""
def create_totp():
    # Crea un oggetto TOTP con la chiave
    totp = pyotp.TOTP(TOTP_KEY, interval=30)
    # Genera un codice TOTP valido ora
    code = totp.now()
    return code