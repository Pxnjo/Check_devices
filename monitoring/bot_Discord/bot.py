# https://discord.com/oauth2/authorize?client_id=1362421532177072420&permissions=2415987904&integration_type=0&scope=bot
# Ottieni la directory del file corrente
# from discord.ext import commands
import discord, threading, subprocess
import time
from datetime import datetime, timedelta
import asyncio, os, sys, re, json
# Ottieni la directory del file corrente
current_dir = os.path.dirname(os.path.abspath(__file__))
# Risali di una directory
parent_dir = os.path.dirname(current_dir)
# Aggiungi la directory parent al path
sys.path.insert(0, parent_dir)
channels_folder = os.path.join(current_dir, 'channels')
log_dir = os.path.join(os.path.dirname(current_dir), 'logs')
mon_dir = os.path.join(os.path.dirname(current_dir), 'mon')
# Ottieni il path della cartella utils
utils_dir = os.path.join(parent_dir, 'utils')
hosts_path = os.path.join(mon_dir, 'hosts.json')
from config import this_machine_hostname
from utils.logger import setup_logger
notifier = None

logger = setup_logger("discord_logger", os.path.join(log_dir, "discord.log"))

TOKEN = "5sy5t4uh56.6e5yzerdhr65.5ahgthes5ya"
# L'ID del canale dove vuoi che il bot risponda
CATEGORY_ID = 1234567890 # Sostituisci con il tuo ID categoria

def create_discord_client():
    intents = discord.Intents.default()
    intents.message_content = True  # Se hai bisogno di leggere i messaggi
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        logger.info(f"Logged in as {client.user}")
        global notifier
        # notifier = DiscordNotifier(client=client, channel=channel, hosts_path=hosts_path)
        notifier = DiscordNotifier(client=client)
        data = notifier.load_data(hosts_path)
        this_device_ip = data.get('this_device_ip', {})
        hosts = data.get('hosts', {})
        to_monitor = data.get('to_monitor', {})
        all_devices = set(this_device_ip.keys()) | set(hosts.keys()) | set(to_monitor.keys())
        for hostname in all_devices:
            await notifier.get_hosts_channel(hostname, CATEGORY_ID)

    @client.event
    async def on_disconnect():
        logger.error(f"{client.user} è stato disconnesso!")

    return client

async def create_channels(hostname):
    await notifier.get_hosts_channel(hostname, CATEGORY_ID)

class DiscordNotifier:
    def __init__(self, client):
        self.client = client
        self.last_sent = {}  # cache interna: {hostname: datetime}

    def load_data(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def save_data(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

    def _should_notify(self, hostname, cooldown_minutes=2):
        now = datetime.now()
        last = self.last_sent.get(hostname)
        if not last or now - last >= timedelta(minutes=cooldown_minutes):
            self.last_sent[hostname] = now
            return True
        return False
    
    async def get_hosts_channel(self, hostname, CATEGORY_ID):
        guild = self.client.guilds[0]  # Prendi il primo server a cui sei collegato

        # 1. Cerco il canale su Discord, nella categoria giusta
        category = self.client.get_channel(CATEGORY_ID)
        if not category:
            logger.error(f"[ERROR] Categoria Discord ID {CATEGORY_ID} non trovata.")
            return None
        for channel in category.text_channels:
            if channel.name.lower() == hostname.lower():
                logger.info(f"[INFO] Trovato canale Discord esistente per {hostname}: {channel.name}")
                return channel.id
        
        # 2. Se non trovato, creo il canale
        logger.error(f"[ERROR] Nessun canale trovato per {hostname}, creazione in corso...")
        channel = await guild.create_text_channel(
            name=hostname,
            category=category
        )
        logger.info(f"[INFO] Creato nuovo canale Discord: {channel.name}")
        return channel.id
    
    async def _notify(self, hostname, full_message, is_error):
        channel_id = await self.get_hosts_channel(hostname, CATEGORY_ID)
        if not channel_id:
            logger.error(f"[ERRORE] Impossibile trovare o creare il canale per {hostname}")
            return

        channel = self.client.get_channel(channel_id)
        if not channel:
            logger.error(f"[ERRORE] ID canale {channel_id} non valido per {hostname}")
            return

        if is_error:
            if self._should_notify(hostname):
                await channel.send(full_message)
        else: # Se è tipo info
            await channel.send(full_message)
            self.last_sent.pop(hostname, None)

    def notify_error(self, hostname, full_message):
        asyncio.run_coroutine_threadsafe(self._notify(hostname, full_message, is_error=True), self.client.loop)

    def notify_info(self, hostname, full_message):
        asyncio.run_coroutine_threadsafe(self._notify(hostname, full_message, is_error=False), self.client.loop)
        self.last_sent.pop(hostname, None)  # resettiamo il cooldown

async def run_discord_bot(token):
    client = create_discord_client()
    try:
        await client.start(token)
    except Exception as e:
        logger.error(f"[{this_machine_hostname}] Errore nel bot Discord: {e}")
    finally:
        if client.is_ready():
            await client.close()
            logger.error(f"[{this_machine_hostname}] BOT Discord chiuso correttamente")

def has_vip(vip):
    result = subprocess.run(
        ["ip", "addr", "show"],
        stdout=subprocess.PIPE,
        text=True
    )
    return vip in result.stdout

async def check_master_status():
    was_online = False
    bot_task = None

    while True:
        is_online = has_vip("203.0.113.1")

        if is_online and not was_online:
            logger.info("Il VIP è online")
            if bot_task is None or bot_task.done():
                # Crea un nuovo task per il bot
                bot_task = asyncio.create_task(run_discord_bot(TOKEN))
    
        elif not is_online and was_online:
            global notifier
            notifier = None

            logger.error("Il VIP non è più online")
            if bot_task and not bot_task.done():
                try:
                    # Cancella il task e aspetta che termini
                    bot_task.cancel()
                    await asyncio.wait_for(asyncio.shield(bot_task), timeout=5)
                except asyncio.TimeoutError:
                    logger.error(f"Forzatura chiusura del bot [{this_machine_hostname}]")
                except asyncio.CancelledError:
                    logger.error(f"Task del bot cancellato [{this_machine_hostname}]")

        was_online = is_online
        await asyncio.sleep(2)

# Variabili per la gestione del thread
bot_thread = None
stop_event = threading.Event()

def run_bot_async():
    """Funzione target per il thread che esegue il loop asyncio"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(check_master_status())
    except Exception as e:
        logger.error(f"Errore nel thread del bot: {e}")
    finally:
        loop.close()

def start_bot():
    """Avvia il bot in un thread separato"""
    global bot_thread, stop_event
    
    # Resetta l'evento di stop
    stop_event.clear()
    
    if bot_thread is None or not bot_thread.is_alive():
        bot_thread = threading.Thread(target=run_bot_async, name="discord_bot")
        bot_thread.daemon = True
        bot_thread.start()
        print(f"[{this_machine_hostname}] Bot Discord avviato")
        return True
    else:
        print("Il bot Discord è già in esecuzione")
        return False

def stop_bot():
    global bot_thread, stop_event

    if bot_thread and bot_thread.is_alive():
        logger.error("Arresto del bot Discord...")
        stop_event.set()
        try:
            bot_thread.join(timeout=5)
        except KeyboardInterrupt:
            logger.error("Interrotto durante la chiusura del thread")
        logger.error("Bot Discord arrestato")
        return True
    else:
        logger.error("Il bot Discord non è in esecuzione")
        return False

# Per l'esecuzione diretta del file
# if __name__ == "__main__":
#     start_bot()
    
#     try:
#         # Manteniamo il programma in esecuzione
#         while not stop_event.is_set():
#             time.sleep(1)
#     except KeyboardInterrupt:
#         print("Interruzione rilevata, arresto del bot...")
#         try:
#             stop_bot()
#         except Exception as e:
#             print(f"Errore durante l'arresto del bot: {e}")

