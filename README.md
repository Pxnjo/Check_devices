# 🚀 Monitoring Script

---

## <span style="color:cyan">**Overview**</span>

This script was born from the need to monitor VMs outside the internal network, devices that support the script, or simple IP-based devices (e.g., IoT).  
(⚡ See the guide carefully as IoT devices have different steps for being monitored.)

**Key Features**:
- 🔔 **Discord notifications**
- 🛡️ **Decentralized architecture** to minimize single points of failure
- 🪶 **Lightweight and secure**

---

## <span style="color:limegreen">**Components**</span>

- 🤖 A **Discord bot** that manages the server
- 🌐 An **API server** for communication and keeping hosts updated
- 🧩 A **client script** that sends requests to the servers

---

## <span style="color:gold">**Getting Started**</span>

Follow this guide carefully, as there are multiple steps to make it work correctly.

### 📦 **Dependencies**
- 🐳 **Docker**

### 🛠️ **Setup Instructions**

1. **Configure** `monitoring/config.py`:
   ```python
   this_machine_hostname = "monitor1"  # Hostname of the current machine
   this_machine_ip = "10.20.30.13"      # IP address of the current machine

   hostname = "monitor2"               # Hostname of the first machine to monitor
   ip = "10.20.30.14"                  # IP address of the first machine to monitor
   ```

2. **Initialize Certificates and TOTP**:
   Run the following command inside the `utils/` folder:
   ```bash
   python3 initialize.py
   ```
   - 🔑 It will generate a **TOTP key** to be set in `TOTP_KEY = ""` inside `config.py`.
   - 📜 It will create **CA certificates** in `server/ssl`.
   - ⚠️ **IMPORTANT:** Save the certificates and the TOTP key securely! They must be identical across all scripts to ensure authentication.

3. **Create a Discord Server** 🎮
   - (If you don't know how, search for a tutorial.)

4. **Create a Bot on Discord Developer Portal** 🛠️
   - Save the **Authentication TOKEN**.
   - 🔒 **Important:** The token must be the same for all scripts.

5. **Set the Token** in `bot_Discord/bot.py`:
   ```python
   TOKEN = "your_discord_bot_token"
   ```

6. **Set the Category ID** 🗂️
   - Create a category on your Discord server.
   - Enable **Developer Mode** in account settings.
   - Right-click the category -> **Copy ID** and set:
   ```python
   CATEGORY_ID = 234564564542397  # Example ID (without quotes)
   ```

7. **Build and Start the Docker Container** 🛠️
   Inside the `Check_devices` folder, run:
   ```bash
   docker compose up -d --build
   ```

---

## <span style="color:orange">**Operation**</span>

At this point, the script should start automatically.  
You should see new channels appear on your Discord server (they may be empty initially since no logs have been generated yet).

✅ Everything from here onwards is **fully automated**.

---

## <span style="color:deepskyblue">**Adding New Devices**</span>

- ➕ **To add fully featured devices:**
  - Save the current script with all the changes in a secure location.
  - Modify only the first four entries of `monitoring/config.py`.

- ➕ **To add IoT or Ping-only devices:**
  - Run the following command inside the `utils/` folder:
    ```bash
    python3 add_device.py
    ```
  - Enter a unique hostname and the device's IP address.

The script will propagate changes automatically, and the new host will be monitored.

---

## <span style="color:tomato">**Removing a Device**</span>

To remove a host, run:
```bash
python3 forgot_device.py
```
inside the `utils/` folder.

---
