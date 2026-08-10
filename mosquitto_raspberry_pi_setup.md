# Installing and Configuring Eclipse Mosquitto MQTT Broker on Raspberry Pi

A complete, step-by-step guide to installing, configuring, and testing the Eclipse Mosquitto MQTT broker on a Raspberry Pi for home automation and IoT projects.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
  - [Step 1: Update System Packages](#step-1-update-system-packages)
  - [Step 2: Install Mosquitto and Client Utilities](#step-2-install-mosquitto-and-client-utilities)
  - [Step 3: Enable and Start Mosquitto Service](#step-3-enable-and-start-mosquitto-service)
  - [Step 4: Configure Remote Access (Mosquitto v2.0+)](#step-4-configure-remote-access-mosquitto-v20)
  - [Step 5: Test the MQTT Broker](#step-5-test-the-mqtt-broker)
- [Security Settings (Optional)](#security-settings-optional)
  - [Enabling Password Authentication](#enabling-password-authentication)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ℹ️ Overview

[Eclipse Mosquitto](https://mosquitto.org/) is a popular, open-source message broker that implements the MQTT protocol versions 5.0, 3.1.1, and 3.1. Lightweight and power-efficient, Mosquitto is ideal for running on Raspberry Pi to connect microcontrollers (ESP32, ESP8266, Arduino), Home Assistant instances, and custom IoT devices across a local network.

---

## ⚡ Prerequisites

- Raspberry Pi running **Raspberry Pi OS** (Debian-based)
- Active network connection (Wi-Fi or Ethernet)
- Terminal access (directly or via SSH)
- Sudo/root permissions

---

## 🚀 Installation Guide

### Step 1: Update System Packages

Ensure package lists and existing system software are up to date to prevent dependency conflicts.

```bash
sudo apt update && sudo apt upgrade -y
```

---

### Step 2: Install Mosquitto and Client Utilities

Install the Mosquitto broker daemon along with `mosquitto-clients` (which includes command-line tools `mosquitto_sub` and `mosquitto_pub` for testing).

```bash
sudo apt install -y mosquitto mosquitto-clients
```

---

### Step 3: Enable and Start Mosquitto Service

Set Mosquitto to start automatically at system boot, then launch the service immediately.

```bash
# Enable auto-start on boot
sudo systemctl enable mosquitto

# Start the Mosquitto service
sudo systemctl start mosquitto
```

To verify that the Mosquitto service is running properly, execute:

```bash
sudo systemctl status mosquitto
```

---

### Step 4: Configure Remote Access (Mosquitto v2.0+)

> [!IMPORTANT]
> Since Mosquitto version 2.0, the broker binds only to `localhost` (`127.0.0.1`) by default and blocks external connections. To allow other devices on your local network to communicate with the Pi, you must explicitly enable remote listening.

1. Create a custom configuration file in `/etc/mosquitto/conf.d/`:

   ```bash
   sudo nano /etc/mosquitto/conf.d/default.conf
   ```

2. Add the following lines to open port `1883` and grant access:

   ```text
   listener 1883
   allow_anonymous true
   ```

3. Save and close the editor (Press `Ctrl + O`, hit `Enter`, then press `Ctrl + X`).

4. Restart Mosquitto to apply the new configuration:

   ```bash
   sudo systemctl restart mosquitto
   ```

---

### Step 5: Test the MQTT Broker

Verify that the broker is processing published messages correctly. Open two separate terminal windows (or SSH sessions).

#### Window 1 — Subscriber

Subscribe to a test topic named `home/test`:

```bash
mosquitto_sub -h localhost -t "home/test"
```

*This terminal session will stay open and wait for incoming messages.*

#### Window 2 — Publisher

In the second window, publish a message to `home/test`:

```bash
mosquitto_pub -h localhost -t "home/test" -m "Hello World from Mosquitto!"
```

**Expected Result:**
In **Window 1**, you should instantly see the string printed:

```text
Hello World from Mosquitto!
```

---

## 🔒 Security Settings (Optional)

### Enabling Password Authentication

Running an anonymous broker is fine for isolated testing, but setting up user credentials is recommended for production environments.

1. **Create a password file and add a user:**

   ```bash
   sudo mosquitto_passwd -c /etc/mosquitto/passwd <your_username>
   ```
   *(You will be prompted to enter and confirm a password).*

2. **Update `/etc/mosquitto/conf.d/default.conf`:**

   ```bash
   sudo nano /etc/mosquitto/conf.d/default.conf
   ```

3. **Change the configuration to:**

   ```text
   listener 1883
   allow_anonymous false
   password_file /etc/mosquitto/passwd
   ```

4. **Restart Mosquitto:**

   ```bash
   sudo systemctl restart mosquitto
   ```

5. **Test authenticated publishing/subscribing:**

   ```bash
   # Subscriber
   mosquitto_sub -h localhost -t "home/test" -u "<your_username>" -P "<your_password>"

   # Publisher
   mosquitto_pub -h localhost -t "home/test" -m "Authenticated message" -u "<your_username>" -P "<your_password>"
   ```

---

## 🛠️ Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **Connection Refused (`111`)** | Mosquitto service isn't running or bound only to localhost | Run `sudo systemctl status mosquitto` and check `/etc/mosquitto/conf.d/default.conf` |
| **Cannot connect from remote IP** | Mosquitto v2.0+ default setting or firewall blocking port 1883 | Ensure `listener 1883` and `allow_anonymous true` are set, and check `ufw` status (`sudo ufw allow 1883/tcp`) |
| **`mosquitto_passwd` command not found** | Missing package | Install via `sudo apt install mosquitto-clients` |

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for more details.
