#!/bin/bash

# Genera il file di configurazione di Keepalived
python3 /monitoring/utils/keepalived.py

keepalived -f /etc/keepalived/keepalived.conf

tmux new-session -d -s monitor 'python3 /monitoring/main.py'

tail -f /dev/null # Serve a non far pegnere subito il docker
