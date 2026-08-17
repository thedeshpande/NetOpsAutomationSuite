# 🛡️ NetOps Automation Suite

A lightweight, Python-based network automation platform designed to simplify and standardize routine network operations such as **Pre-Check**, **Post-Check**, and **Backup**. The suite provides a clean web interface to select operations, scope target devices, execute commands via SSH, and seamlessly retry failed devices.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0+-black?logo=flask)
![Netmiko](https://img.shields.io/badge/Netmiko-SSH-orange)

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Installation & Setup (Windows)](#installation--setup-windows)
6. [Manual Setup (CLI)](#manual-setup-cli)
7. [How to Run](#how-to-run)
8. [Using the Web UI](#using-the-web-ui)
9. [Inventory & Device Profiles](#inventory--device-profiles)
10. [Retry Logic & Results](#retry-logic--results)
11. [Troubleshooting](#troubleshooting)
12. [Development Workflow](#development-workflow)
13. [Important Considerations](#important-considerations)
14. [Future Enhancements](#future-enhancements)

---

## 📖 Overview
Managing network infrastructure manually across multiple sites is slow and error-prone. The **NetOps Automation Suite** connects to your network inventory, allows you to filter devices by Site and Category, and executes predefined command workflows. 

It tracks success/failure at the device level and provides one-click summaries to copy into incident chats or emails.

---

## ✨ Key Features
- **Core Operations:** Supports Pre-Check, Post-Check, and Backup workflows.
- **Scoped Execution:** Filter targets by Site, Category, Profile, or Vendor.
- **Device Preview:** Always review exactly which devices will be affected before executing.
- **Execution Tracking:** Every run gets a unique ID (e.g., `EXEC-20260817-154618`) for traceability.
- **Smart Retry:** If devices fail, the suite retries *only* the failed devices (up to 3 attempts) without re-running successful ones.
- **Clean Reporting:** Copy full execution summaries or just failed device details in a clean, plaintext format optimized for Teams/Slack.
- **Failure Parsing:** Translates messy SSH/Netmiko exceptions into clean, readable failure reasons (e.g., "Authentication Failed").
- **Automated Setup:** Includes a one-click setup wizard to configure the Python environment on Windows.

---

## 🛠 Architecture
The application is divided into logical layers to ensure maintainability and separation of responsibilities.

```text
+-------------------------------------------------------+
|                    Web UI                             |
|              HTML / CSS / JavaScript                  |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|                 Flask Web Layer                       |
|                    web/app.py                         |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|              Operation Layer                          |
|       Precheck / Postcheck / Backup                   |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|               Execution Layer                         |
|                 core/executor.py                      |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|             Network Connectivity                      |
|                  Netmiko / SSH                        |
+-------------------------------------------------------+
                         |
                         v
+-------------------------------------------------------+
|                 Network Devices                       |
+-------------------------------------------------------+
```

### Project Structure
```text
NetOpsAutomationSuite/
│
├── .venv/                     # Auto-generated virtual environment
├── core/                       # Execution engine, filters, inventory loading
├── models/                     # Device data models
├── operations/                 # Precheck, Postcheck, Backup logic
├── web/                        # Flask app and static UI files
│   ├── app.py
│   ├── templates/
│   └── static/
├── reports/                    # Auto-generated execution reports
├── inventory/                  # Device inventory source files
├── requirements.txt            # Python dependencies
├── SETUP_NETOPS.bat            # One-time Windows setup wizard
└── START_NETOPS.bat            # Windows daily launcher
```

---

## ⚙️ Prerequisites
Before you begin, ensure you have the following:
1. **Python 3.8+** installed and added to PATH.
2. **Network Connectivity:** VPN connection if target devices are behind a corporate network.
3. **SSH Access:** Valid credentials and management IP reachability for target devices.
4. **Inventory File:** A configured device inventory (Excel/CSV) placed in the `inventory/` folder.

---

## 🚀 Installation & Setup (Windows)

This project includes an automated setup wizard. You only need to run this **once**.

1. Clone or download this repository to your local machine.
2. Double-click the **`SETUP_NETOPS.bat`** file.
3. The setup wizard will automatically execute the following flow:

```text
Check Python
   v
Check requirements.txt
   v
Create .venv if missing
   v
Upgrade pip
   v
Install requirements.txt
   v
Verify Flask
   v
Setup Complete
```

Once the wizard displays **"Setup is complete. Everything is installed successfully!"**, your environment is ready. You can proceed to the "How to Run" section.

---

## 💻 Manual Setup (CLI)
If you prefer the terminal, or are using Mac/Linux, execute these commands:

```bash
# 1. Navigate to the project folder
cd NetOpsAutomationSuite

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Mac/Linux:
source .venv/bin/activate

# 4. Install dependencies
python -m pip install -r requirements.txt
```
*(Note: Always use `python -m pip` instead of just `pip` to ensure packages are installed into the correct virtual environment).*

---

## ▶️ How to Run

### Method 1: One-Click Launcher (Windows)
After running the setup script once, you no longer need to use the terminal.
1. Double-click the **`START_NETOPS.bat`** file. 
2. A terminal window will open, starting the Flask server.
3. Your default web browser will automatically launch the dashboard at `http://127.0.0.1:5000`.
4. Close the terminal window when you are done using the tool.

*(Tip: Right-click `START_NETOPS.bat`, select **Send to -> Desktop (create shortcut)** for easy daily access!)*

### Method 2: Via Command Line
If you prefer the terminal or are on Mac/Linux:
```bash
# 1. Activate the virtual environment (see Manual Setup above)

# 2. Start the application
python web/app.py

# 3. Open your browser to http://127.0.0.1:5000
```

---

## 📖 Using the Web UI

The operator workflow is designed to be safe, preview-driven, and transparent.

1. **Select Operation:** Choose between Pre-Check, Post-Check, or Backup.
2. **Select Site:** Choose a specific site (e.g., `LAB`) or `All Sites`.
3. **Select Category:** Choose a device type (e.g., `Router`) or `All Devices`.
4. **Preview Devices:** Review the filtered list of devices and their IPs. **Always verify this list before executing.**
5. **Run Operation:** Click the execute button (e.g., `▶ RUN PRE-CHECK`).
6. **Review Results:** View the execution summary, including total devices, successful, and failed statuses.
7. **Filter/Search:** Use the UI filters to isolate `Success` or `Failed` devices, or search by Hostname/IP.

---

## 📊 Inventory & Device Profiles

The suite relies on a structured inventory file placed in the `inventory/` folder. A device record must contain the following conceptual fields:

| Hostname | IP Address | Site | Category | Profile | Vendor |
| :--- | :--- | :--- | :--- | :--- | :--- |
| R1 | 10.161.44.200 | LAB | Router | IOS_ROUTER | Cisco |
| SW1 | 10.161.44.201 | LAB | Switch | IOS_SWITCH | Cisco |

### Categories vs. Profiles
- **Category:** The high-level device type (e.g., `Router`, `Switch`, `Firewall`). This is what the UI filters by.
- **Profile:** The specific OS/Driver mapping used by Netmiko (e.g., `IOS_ROUTER`, `CEDGE`, `AIREOS`). 

A single Category can contain multiple Profiles. For example, selecting the `Router` category might execute commands against `IOS_ROUTER` and `CEDGE` profiles simultaneously.

---

## 🔄 Retry Logic & Results

### Smart Retry
If devices fail during execution, the UI will prompt you with a **Retry** option. 
- **No redundant runs:** The suite only retries devices that returned a `FAILED` status. Successful devices are skipped during retries.
- **Limit:** A maximum of 3 retry attempts are allowed. If a device still fails after 3 attempts, the operator is instructed to investigate manually.

### Failure Reason Formatting
Instead of copying long, raw Python exception tracebacks, the suite parses common SSH/Netmiko errors into clean, readable reasons for communication:
- `Authentication Failed`
- `Connection Timed Out`
- `Connection Refused`
- `Network Unreachable`

### Copy Results for Communication
- **Copy Results:** Copies the full execution summary (Successes and Failures) including the Execution ID.
- **Copy Failed:** Copies a clean, simplified list of *only* the failed devices and their concise failure reasons.

**Example Copy Failed Output:**
```text
NetOps Automation Suite
FAILED DEVICES STATUS
----------------------------------------
Site        : LAB
Operation   : PRE-CHECK
Category    : Router
Execution ID: EXEC-20260817-154618
Retry Attempt: 0 / 3

Failed Devices: 1

Device Status
----------------------------------------
Hostname : R1
IP       : 10.161.44.200
Status   : FAILED
Reason   : Authentication Failed
```

---

## 🛠 Troubleshooting

**1. "Virtual environment not found" error when running `START_NETOPS.bat`**
- Ensure you have run `SETUP_NETOPS.bat` first. The setup script creates the `.venv` folder required to launch.

**2. "ModuleNotFoundError: No module named 'flask'"**
- The virtual environment is not active, or dependencies were not installed. Run `SETUP_NETOPS.bat` again, or run `python -m pip install -r requirements.txt` manually.

**3. "Fatal error in launcher: Unable to create process..."**
- This happens when `pip` breaks. Always use `python -m pip` instead of just `pip` when working inside virtual environments.

**4. Device status returns "Authentication Failed"**
- Verify the SSH credentials configured for the device are correct.
- Verify the device IP in the inventory is accurate.
- Ensure the correct device **Profile** is assigned in the inventory.

**5. Device status returns "Connection Timed Out" / "Network Unreachable"**
- Ensure your corporate VPN is connected if the devices are internal.
- Test reachability manually: `ping <device-ip>` from your command line.
- Ensure firewalls between your workstation and the device allow TCP port 22 (SSH).

**6. Browser does not open automatically**
- Wait a few seconds after the terminal window opens. If it still doesn't open, manually navigate to `http://127.0.0.1:5000` in your browser.

---

## 🧑‍💻 Development Workflow

The suite is designed to be highly modular. If you wish to extend its functionality:

**Adding a New Operation:**
1. Create a new module in `operations/` (e.g., `operations/new_op.py`).
2. Define the specific command workflow.
3. Map it to the execution engine in `core/executor.py`.
4. Add the operation to the Flask backend in `web/app.py`.
5. Add the UI button in `web/templates/index.html`.

**Adding a New Device Profile:**
1. Ensure the profile string (e.g., `NEXUS_SWITCH`) is present in your inventory file.
2. Map the profile to the correct Netmiko device type in your configuration/logic.
3. Update command definitions if the new profile requires different CLI syntax.

---

## ⚠️ Important Considerations

1. **VPN & Network Routes:** The automation runs locally on your workstation. If target devices are behind a corporate VPN, connect to the VPN *before* launching the tool.
2. **Security:** Do NOT hardcode device credentials into Git repositories, HTML, or JavaScript. Use protected configuration files excluded via `.gitignore`.
3. **Flask Development Server:** This tool uses the built-in Flask server intended for local/internal use. It is not designed to be exposed to the public internet.
4. **Execution Time:** Depending on the operation and device count, execution may take time. Do not refresh the browser while an operation is in progress.

---

## 🔮 Future Enhancements
- **Authentication:** Add role-based access (Admin, Operator, Viewer).
- **Scheduling:** Allow daily/weekly automated pre-checks and backups.
- **Persistent Database:** Move execution history from flat files to a database (SQLite/PostgreSQL).
- **Notifications:** Integrate execution results directly with Slack, Teams, or ServiceNow.
- **Dashboard:** Add a landing page showing total devices, recent executions, and overall network health.
```