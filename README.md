# NetOps Automation Suite

A lightweight network automation platform designed to simplify and
standardize common network device operations such as **Pre-Check,
Post-Check, and Backup**.

The suite provides a web-based UI for selecting the required operation,
site, and device category, previewing the devices in scope, executing
the operation, viewing device-level results, copying results for
email/chat communication, and retrying failed devices without rerunning
successful devices.

------------------------------------------------------------------------

## Table of Contents

1.  [Overview](#overview)
2.  [Key Features](#key-features)
3.  [How the Suite Works](#how-the-suite-works)
4.  [Architecture](#architecture)
5.  [Project Structure](#project-structure)
6.  [Prerequisites](#prerequisites)
7.  [Installation](#installation)
8.  [Virtual Environment](#virtual-environment)
9.  [Dependencies](#dependencies)
10. [Inventory](#inventory)
11. [Device Model](#device-model)
12. [Filtering](#filtering)
13. [Operations](#operations)
14. [Execution Engine](#execution-engine)
15. [Web Application](#web-application)
16. [API Endpoints](#api-endpoints)
17. [Running the Application](#running-the-application)
18. [One-Click Desktop Launcher](#one-click-desktop-launcher)
19. [Using the Web UI](#using-the-web-ui)
20. [Pre-Check Workflow](#pre-check-workflow)
21. [Post-Check Workflow](#post-check-workflow)
22. [Backup Workflow](#backup-workflow)
23. [Retry Failed Devices](#retry-failed-devices)
24. [Copy Results](#copy-results)
25. [Reports and Output](#reports-and-output)
26. [Execution ID](#execution-id)
27. [Authentication and Credentials](#authentication-and-credentials)
28. [VPN and Network Connectivity](#vpn-and-network-connectivity)
29. [Troubleshooting](#troubleshooting)
30. [Development Workflow](#development-workflow)
31. [Adding a New Operation](#adding-a-new-operation)
32. [Adding a New Device Profile](#adding-a-new-device-profile)
33. [Security Considerations](#security-considerations)
34. [Operational Best Practices](#operational-best-practices)
35. [Known Limitations](#known-limitations)
36. [Future Enhancements](#future-enhancements)
37. [Quick Start](#quick-start)
38. [Conclusion](#conclusion)

------------------------------------------------------------------------

# Overview

## What is NetOps Automation Suite?

NetOps Automation Suite is a Python-based network automation application
that provides a simple interface for performing repetitive network
operations against a defined inventory of network devices.

Instead of manually connecting to every device and running the same
commands, an operator can:

1.  Open the application.
2.  Select an operation.
3.  Select a site.
4.  Select a device category.
5.  Preview the devices that will be affected.
6.  Confirm the operation.
7.  Execute the automation.
8.  Review device-level results.
9.  Retry only failed devices when required.
10. Copy a clean execution summary for communication.

The application uses a Flask web interface and a Python automation
backend.

------------------------------------------------------------------------

# Key Features

## Core Operations

The suite currently supports:

-   **Pre-Check**
-   **Post-Check**
-   **Backup**

## Device Selection

Devices can be scoped using:

-   Site
-   Device Category

The application previews the devices before execution.

## Execution Tracking

Each execution receives a unique Execution ID.

Example:

``` text
EXEC-20260817-154618
```

This makes it easier to identify and communicate a particular automation
run.

## Device-Level Results

Each device can return a status such as:

``` text
SUCCESS
FAILED
SKIPPED
```

The UI displays:

-   Hostname
-   IP address
-   Status
-   Failure reason

## Retry Failed Devices

If some devices fail:

-   Successful devices are not executed again.
-   Only failed devices are sent for retry.
-   Retry attempts are tracked.
-   Maximum retry attempts are limited to 3.
-   If the retry succeeds, the final summary is updated.
-   If devices continue to fail, they remain visible.
-   After the maximum retry count, the operator is instructed to
    investigate manually.

## Copy Results

The application provides a **Copy Results** function for sharing the
complete execution summary.

## Copy Failed

The application provides a **Copy Failed** function for sharing only
currently failed devices.

The copied failure information is intentionally simplified for
email/chat communication.

For example:

``` text
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

----------------------------------------
NetOps Automation Suite
```

------------------------------------------------------------------------

# How the Suite Works

The high-level workflow is:

``` text
User
  |
  v
Web Browser
  |
  v
Flask Web Application
  |
  v
Inventory
  |
  v
Device Filtering
  |
  v
Operation Selection
  |
  v
Executor
  |
  v
Netmiko / SSH
  |
  v
Network Devices
  |
  v
Execution Results
  |
  +--------------------+
  |                    |
  v                    v
Success              Failed
                         |
                         v
                 Retry Failed Devices
                         |
                         v
                    Final Result
```

------------------------------------------------------------------------

# Architecture

The application is divided into logical layers.

``` text
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

Supporting components include:

``` text
Inventory
Filters
Device Model
Command/Profile Definitions
Output/Reporting
```

------------------------------------------------------------------------

# Project Structure

A typical project structure is:

``` text
NetOpsAutomationSuite/
│
├── .venv/
│
├── core/
│   ├── __init__.py
│   ├── inventory.py
│   ├── filters.py
│   ├── executor.py
│   ├── menu.py
│   └── reports.py
│
├── models/
│   ├── __init__.py
│   └── device.py
│
├── operations/
│   ├── __init__.py
│   ├── precheck.py
│   ├── postcheck.py
│   └── backup.py
│
├── web/
│   ├── app.py
│   │
│   ├── templates/
│   │   └── index.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       │
│       └── js/
│           └── app.js
│
├── reports/
│
├── inventory/
│
├── requirements.txt
│
└── START_NETOPS.bat
```

> The exact inventory filename and any additional project files depend
> on the current implementation.

------------------------------------------------------------------------

# Prerequisites

The application requires:

-   Windows workstation
-   Python installed
-   Network connectivity to the target devices
-   VPN connectivity when target devices are reachable only through the
    corporate network
-   SSH access to the target devices
-   Valid network device credentials
-   Project dependencies installed

Python is used for:

-   Flask
-   Inventory processing
-   Device filtering
-   SSH/network automation
-   Execution management
-   Result processing

------------------------------------------------------------------------

# Installation

## 1. Clone or copy the project

Place the project in a directory such as:

``` text
C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite
```

## 2. Open PowerShell

Navigate to the project:

``` powershell
cd C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite
```

## 3. Create a virtual environment

If the project does not already have one:

``` powershell
python -m venv .venv
```

## 4. Activate the virtual environment

``` powershell
.\.venv\Scripts\Activate.ps1
```

You should see:

``` text
(.venv) PS C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite>
```

## 5. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

Using:

``` powershell
python -m pip
```

is preferred over directly using `pip`, because it guarantees that pip
belongs to the currently selected Python interpreter.

------------------------------------------------------------------------

# Virtual Environment

The project uses a local virtual environment:

``` text
.venv\
```

The important executable is:

``` text
.venv\Scripts\python.exe
```

Verify it with:

``` powershell
python -c "import sys; print(sys.executable)"
```

Expected:

``` text
C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite\.venv\Scripts\python.exe
```

Verify Flask:

``` powershell
python -c "import flask; print(flask.__version__)"
```

If the virtual environment is active, Flask should be available.

------------------------------------------------------------------------

# Dependencies

The project uses packages including:

-   Flask
-   Netmiko
-   Paramiko
-   TextFSM
-   ntc-templates
-   pandas
-   openpyxl
-   PyYAML
-   questionary
-   rich
-   cryptography
-   bcrypt
-   scp

The complete dependency list should be maintained in:

``` text
requirements.txt
```

To regenerate it from the currently active environment:

``` powershell
python -m pip freeze > requirements.txt
```

Do this only when you intentionally want to update the project's pinned
dependency list.

------------------------------------------------------------------------

# Inventory

The inventory is the source of truth for devices that the automation can
operate against.

A device record typically contains information such as:

``` text
Hostname
IP Address
Site
Category
Profile
Vendor
```

Example conceptual record:

``` text
Hostname : R1
IP       : 10.161.44.200
Site     : LAB
Category : Router
Profile  : IOS_ROUTER
Vendor   : Cisco
```

The inventory layer is responsible for loading device information.

It should not be responsible for:

-   SSH connections
-   Command execution
-   Pre-check logic
-   Post-check logic
-   Backup logic

------------------------------------------------------------------------

# Device Model

The `models/device.py` module represents a network device as a Python
object.

The device model keeps device attributes together so that the rest of
the application can work with structured device objects rather than raw
Excel rows or dictionaries.

Conceptually:

``` text
Device
 |
 +-- hostname
 +-- ip
 +-- site
 +-- category
 +-- profile
 +-- vendor
```

------------------------------------------------------------------------

# Filtering

The filtering engine is located in:

``` text
core/filters.py
```

The `DeviceFilter` supports filtering by:

-   Site
-   Category
-   Profile
-   Vendor
-   Hostname

The primary UI workflow uses:

``` text
Site + Category
```

Examples:

``` text
LAB + Router
```

or:

``` text
All + Router
```

or:

``` text
All + All
```

When `All` is selected, that particular filter is not applied.

The final device list is sorted by hostname.

------------------------------------------------------------------------

# Operations

Operations are separated into individual modules.

``` text
operations/
│
├── precheck.py
├── postcheck.py
└── backup.py
```

This separation keeps operation-specific workflow logic outside the
Flask application.

------------------------------------------------------------------------

# Pre-Check

Pre-Check is intended to collect the required pre-operation information
from selected devices.

The workflow is:

``` text
Select Pre-Check
      |
      v
Select Site
      |
      v
Select Category
      |
      v
Preview Devices
      |
      v
Confirm
      |
      v
Executor
      |
      v
Network Devices
      |
      v
Results
```

------------------------------------------------------------------------

# Post-Check

Post-Check follows the same execution architecture.

The purpose is to collect post-operation state from the selected
devices.

Workflow:

``` text
Post-Check
    |
    v
Site + Category
    |
    v
Device Preview
    |
    v
Execution
    |
    v
Results
```

------------------------------------------------------------------------

# Backup

Backup uses the same execution framework but performs the
backup-specific command workflow.

Workflow:

``` text
Backup
   |
   v
Site + Category
   |
   v
Device Preview
   |
   v
Execution
   |
   v
Backup Output
```

------------------------------------------------------------------------

# Execution Engine

The main execution engine is:

``` text
core/executor.py
```

The Executor is responsible for the actual device execution workflow.

Conceptually:

``` text
Executor
   |
   +-- Receive devices
   |
   +-- Receive operation
   |
   +-- Connect to device
   |
   +-- Execute commands
   |
   +-- Capture output
   |
   +-- Determine status
   |
   +-- Return structured result
```

The executor should remain independent of the web interface.

This allows the same execution engine to be reused by:

-   CLI workflows
-   Flask UI
-   Future APIs
-   Future scheduling mechanisms

------------------------------------------------------------------------

# Web Application

The Flask application is:

``` text
web/app.py
```

It provides the HTTP interface between the browser and Python automation
engine.

The browser communicates with Flask using HTTP requests.

Conceptually:

``` text
Browser
   |
   | HTTP
   v
Flask
   |
   v
Python Automation
```

------------------------------------------------------------------------

# API Endpoints

The web application exposes endpoints for UI operations.

## Inventory

The UI requests inventory information from the Flask backend.

Conceptually:

``` text
GET /api/inventory
```

The response provides the devices and available selection values
required by the UI.

------------------------------------------------------------------------

## Execute

The main execution endpoint is:

``` text
POST /api/execute
```

The UI sends information such as:

``` json
{
    "operation": "precheck",
    "site": "LAB",
    "category": "Router"
}
```

Flask then:

1.  Loads inventory.
2.  Applies the selected scope.
3.  Generates an execution ID.
4.  Calls the appropriate operation.
5.  Returns the results.

------------------------------------------------------------------------

## Retry

The retry endpoint is:

``` text
POST /api/retry
```

The UI sends only the failed devices.

Conceptually:

``` json
{
    "operation": "precheck",
    "site": "LAB",
    "category": "Router",
    "execution_id": "EXEC-20260817-154618",
    "failed_devices": [
        {
            "hostname": "R1",
            "ip": "10.161.44.200"
        }
    ]
}
```

The backend maps those devices back to the inventory and executes only
those devices.

This is important because successful devices should not be unnecessarily
executed again.

------------------------------------------------------------------------

# Running the Application

## Manual method

Activate the virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Then run:

``` powershell
python web/app.py
```

Flask will normally start at:

``` text
http://127.0.0.1:5000
```

Open the URL in a browser.

------------------------------------------------------------------------

# One-Click Desktop Launcher

The project includes a Windows batch launcher:

``` text
START_NETOPS.bat
```

The launcher can be placed on the Windows Desktop.

The project itself remains in:

``` text
C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite
```

The launcher points to that project directory.

## Example launcher

``` bat
@echo off

title NetOps Automation Suite

set "PROJECT_DIR=C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite"

echo.
echo ============================================================
echo              NETOPS AUTOMATION SUITE
echo ============================================================
echo.

if not exist "%PROJECT_DIR%\.venv\Scripts\python.exe" (

    echo ERROR: Virtual environment not found.
    echo.
    echo Expected:
    echo %PROJECT_DIR%\.venv\Scripts\python.exe
    echo.

    pause
    exit /b 1
)

echo Virtual environment found.
echo.

echo Starting Flask server...
echo.

start "NetOps Flask Server" cmd /k ""%PROJECT_DIR%\.venv\Scripts\python.exe" "%PROJECT_DIR%\web\app.py""

echo Waiting for Flask server...

:WAIT_FOR_SERVER

powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:5000' -UseBasicParsing -TimeoutSec 1 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1

if errorlevel 1 (

    timeout /t 1 /nobreak >nul

    goto WAIT_FOR_SERVER
)

echo.
echo Flask server is ready.
echo Opening NetOps Automation Suite...
echo.

start "" "http://127.0.0.1:5000"

echo.
echo ============================================================
echo              APPLICATION STARTED
echo ============================================================
echo.
echo Browser:
echo http://127.0.0.1:5000
echo.
echo Keep the Flask server window running.
echo ============================================================
echo.

exit /b 0
```

## How the launcher works

``` text
Double-click START_NETOPS.bat
             |
             v
Locate project directory
             |
             v
Verify .venv
             |
             v
Start web/app.py
             |
             v
Wait for port 5000
             |
             v
Open browser automatically
             |
             v
http://127.0.0.1:5000
```

The launcher avoids manually typing:

``` powershell
python web/app.py
```

and manually opening:

``` text
http://127.0.0.1:5000
```

------------------------------------------------------------------------

# Using the Web UI

## Step 1 --- Select Operation

Choose one:

``` text
Pre-Check
Post-Check
Backup
```

------------------------------------------------------------------------

## Step 2 --- Select Site

Example:

``` text
LAB
```

or:

``` text
All Sites
```

------------------------------------------------------------------------

## Step 3 --- Select Device Category

Example:

``` text
Router
```

or:

``` text
All Devices
```

------------------------------------------------------------------------

## Step 4 --- Preview Devices

The UI displays the devices that match the selected scope.

Example:

``` text
Hostname    IP Address       Category    Profile
R1          10.161.44.200    Router      IOS_ROUTER
R2          10.161.44.201    Router      IOS_ROUTER
```

Always review this list before executing an operation.

------------------------------------------------------------------------

## Step 5 --- Run Operation

The button changes based on the selected operation.

For example:

``` text
▶ RUN PRE-CHECK
```

or:

``` text
▶ RUN POST-CHECK
```

or:

``` text
▶ RUN BACKUP
```

The application asks for confirmation before execution.

------------------------------------------------------------------------

# Execution Result

After execution, the UI displays:

``` text
EXECUTION RESULT

Site          : LAB
Operation     : PRE-CHECK
Category      : Router
Execution ID  : EXEC-20260817-154618

Total Devices : 10
Successful    : 9
Failed        : 1
```

The device-level table then shows the individual status.

Example:

``` text
Hostname    IP Address       Status
R1          10.161.44.200    SUCCESS
R2          10.161.44.201    SUCCESS
CORE        10.161.44.202    FAILED
```

------------------------------------------------------------------------

# Result Filters

The result table supports filtering:

``` text
All
Success
Failed
```

This allows the operator to quickly isolate failed devices.

------------------------------------------------------------------------

# Result Search

The result search can be used to find devices by:

-   Hostname
-   IP address

Example:

``` text
CORE
```

or:

``` text
10.161.44.202
```

------------------------------------------------------------------------

# Retry Failed Devices

If one or more devices fail, the UI displays:

``` text
⚠ Failed Devices

1 device(s) failed during the operation.

Would you like to retry the remaining failed device(s) again?

[ RETRY FAILED DEVICES ]
[ COPY FAILED ]
[ CANCEL ]
```

## Retry behavior

The retry operation does **not** rerun the entire original scope.

Example:

``` text
Original:

R1  SUCCESS
R2  SUCCESS
R3  FAILED
R4  SUCCESS
```

Retry:

``` text
R3 ONLY
```

R1, R2, and R4 are not executed again.

------------------------------------------------------------------------

# Retry Attempts

The suite allows a maximum of:

``` text
3 retry attempts
```

Example:

``` text
Initial execution
10 total
9 success
1 failed

Retry Attempt 1
10 total
9 success
1 failed

Retry Attempt 2
10 total
10 success
0 failed
```

When all devices recover:

``` text
SUCCESS
```

The retry section disappears.

If the device continues failing after three attempts:

``` text
Maximum retry attempts reached.

Please investigate the remaining failed device(s) manually.
```

------------------------------------------------------------------------

# Copy Results

The **Copy Results** button copies the overall execution summary.

Example:

``` text
NetOps Automation Suite
----------------------------------------
Site        : LAB
Operation   : PRECHECK
Category    : Router
Execution ID: EXEC-20260817-154618

Total Devices : 1
Successful    : 0
Failed        : 1

Device Status
----------------------------------------
R1    10.161.44.200    FAILED
```

This is intended for:

-   Email
-   Microsoft Teams
-   Chat
-   Ticket updates
-   Operational communication

------------------------------------------------------------------------

# Copy Failed

The **Copy Failed** button copies only the currently failed devices.

Example:

``` text
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

----------------------------------------
NetOps Automation Suite
```

This is intentionally cleaner than the full internal network-library
exception.

------------------------------------------------------------------------

# Failure Reason Formatting

The UI recognizes common network execution failures.

Examples:

``` text
Authentication Failed
Connection Timed Out
Connection Refused
Network Unreachable
Device Unreachable
```

Instead of copying a long diagnostic exception, the communication output
uses a concise reason.

The detailed error can still be retained by the underlying execution
result/logging workflow.

------------------------------------------------------------------------

# Reports and Output

The project can maintain execution-related output under:

``` text
reports/
```

Reports can be organized by date.

Conceptually:

``` text
reports/
│
├── 2026-08-17/
│   ├── PRECHECK_...
│   ├── POSTCHECK_...
│   └── BACKUP_...
│
└── ...
```

The exact report structure depends on the current `ReportManager`
implementation.

------------------------------------------------------------------------

# Execution ID

Every execution is associated with a unique identifier.

Example:

``` text
EXEC-20260817-154618
```

The Execution ID helps with:

-   Troubleshooting
-   Communication
-   Tracking a particular run
-   Correlating execution output
-   Identifying retry activity

A typical identifier contains:

``` text
EXEC
+
DATE
+
TIME
```

Example:

``` text
EXEC-20260817-154618
```

------------------------------------------------------------------------

# Authentication and Credentials

Network connectivity generally requires valid credentials for the target
devices.

Credentials should **not** be hardcoded into:

-   JavaScript
-   HTML
-   Git repositories
-   README files
-   Screenshots
-   Shared configuration files

Do not commit real passwords or private keys.

If credentials are currently stored in an inventory/configuration
mechanism, ensure that the file is protected and excluded from source
control where appropriate.

------------------------------------------------------------------------

# VPN and Network Connectivity

The automation runs from the workstation where the Python application is
running.

If target devices are accessible only through a corporate VPN:

``` text
Office Laptop
     |
     v
Corporate VPN
     |
     v
Corporate Network
     |
     v
Network Device
```

The VPN must provide the workstation with a route to the target device
networks.

In a normal VPN setup, you generally do not manually add Windows routes
if the VPN client already installs the required routes.

Before running automation, verify connectivity.

For example:

``` powershell
ping 10.161.44.200
```

or test TCP/SSH reachability where ICMP is unavailable.

The important requirement is that the workstation can actually reach the
target device's management IP and SSH port.

------------------------------------------------------------------------

# Troubleshooting

## Flask does not start

Check that the virtual environment is active:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Then:

``` powershell
python -c "import sys; print(sys.executable)"
```

The result should point to:

``` text
NetOpsAutomationSuite\.venv\Scripts\python.exe
```

Then:

``` powershell
python web/app.py
```

------------------------------------------------------------------------

## Flask module not found

Example:

``` text
ModuleNotFoundError: No module named 'flask'
```

Activate the virtual environment:

``` powershell
.\.venv\Scripts\Activate.ps1
```

Then install dependencies:

``` powershell
python -m pip install -r requirements.txt
```

------------------------------------------------------------------------

## `pip` launcher error

If you see something similar to:

``` text
Fatal error in launcher:
Unable to create process...
```

avoid relying on the standalone `pip` command.

Use:

``` powershell
python -m pip install flask
```

or:

``` powershell
python -m pip freeze
```

This ensures pip runs under the selected Python interpreter.

------------------------------------------------------------------------

## Browser does not open

Try:

``` text
http://127.0.0.1:5000
```

If the page does not load, check the Flask terminal.

You should see something similar to:

``` text
Running on http://127.0.0.1:5000
```

------------------------------------------------------------------------

## BAT file says virtual environment not found

The launcher uses:

``` text
C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite
```

as the project directory.

Verify:

``` text
C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite\.venv\Scripts\python.exe
```

exists.

If the project is moved, update the `PROJECT_DIR` value in the BAT file.

------------------------------------------------------------------------

## Device authentication failed

Example:

``` text
Authentication Failed
```

Possible causes include:

-   Incorrect username
-   Incorrect password
-   Incorrect authentication method
-   Incorrect SSH key
-   Wrong device IP
-   Wrong device profile
-   Device-side authentication restrictions

Verify credentials and device information.

------------------------------------------------------------------------

## Device cannot be reached

Check:

1.  VPN connection
2.  Device IP
3.  Windows routing
4.  Firewall restrictions
5.  SSH port
6.  Device management interface
7.  Corporate network access

------------------------------------------------------------------------

## Retry still fails

If a device continues failing:

``` text
Initial
  ↓
Retry 1
  ↓
Retry 2
  ↓
Retry 3
```

After three retries, investigate the device manually.

Repeated retry attempts should not replace troubleshooting of an actual
device/network problem.

------------------------------------------------------------------------

# Development Workflow

When modifying the project:

``` text
1. Activate .venv
2. Make code changes
3. Start Flask
4. Test UI
5. Test operation
6. Test failure scenario
7. Test retry
8. Test copy output
9. Review logs
10. Commit changes
```

Start development server:

``` powershell
python web/app.py
```

Stop it:

``` text
CTRL + C
```

------------------------------------------------------------------------

# Adding a New Operation

Operations are separated into:

``` text
operations/
```

To add a new operation:

1.  Create a new operation module.
2.  Define its workflow.
3.  Connect it to the executor.
4.  Add it to Flask.
5.  Add the operation to the UI.
6.  Test normal execution.
7.  Test failure handling.
8.  Test retry behavior.
9.  Update documentation.

For example:

``` text
operations/
├── precheck.py
├── postcheck.py
├── backup.py
└── new_operation.py
```

The operation should reuse the common execution framework where
possible.

------------------------------------------------------------------------

# Adding a New Device Profile

Profiles allow different device types or command sets to be handled
appropriately.

Examples may include:

``` text
IOS_ROUTER
IOS_SWITCH
CEDGE
VEDGE
AIREOS
```

Category and Profile should remain conceptually separate.

For example:

``` text
Category = Router
```

can contain multiple profiles:

``` text
IOS_ROUTER
CEDGE
VEDGE
```

Selecting:

``` text
Router
```

should therefore include all appropriate Router profiles.

------------------------------------------------------------------------

# Security Considerations

## Principle of Least Privilege

Use the minimum permissions required for:

-   Network device accounts
-   File access
-   Application execution
-   Inventory access

## Credentials

Never commit:

``` text
passwords
private keys
tokens
API keys
```

to Git.

## Source Control

Use `.gitignore` for sensitive/local files such as:

``` text
.venv/
__pycache__/
*.pyc
.env
credentials files
local inventory files
runtime output
```

Adjust the list according to the actual project requirements.

## Flask Development Server

The built-in Flask server is suitable for local development and internal
tooling.

It should not automatically be treated as a production-grade public web
server.

The application is currently intended to run locally:

``` text
127.0.0.1:5000
```

------------------------------------------------------------------------

# Operational Best Practices

Before executing an operation:

1.  Verify VPN connectivity.
2.  Verify device inventory.
3.  Select the correct site.
4.  Select the correct category.
5.  Review the device preview.
6.  Confirm the operation.
7.  Monitor the execution result.

After execution:

1.  Review successful devices.
2.  Review failed devices.
3.  Retry only when appropriate.
4.  Copy failed-device information for communication.
5.  Investigate persistent failures.
6.  Preserve the Execution ID for tracking.

------------------------------------------------------------------------

# Known Limitations

The current application is designed as a local/internal automation
suite.

Current limitations may include:

-   Flask development server is used locally.
-   Browser access is local to the workstation.
-   Network access depends on workstation/VPN connectivity.
-   Device credentials must be available to the automation workflow.
-   Retry is limited to three attempts.
-   Persistent enterprise audit/database functionality is not currently
    part of the core workflow.
-   Concurrent multi-user execution is not the primary design target.
-   The exact command set depends on the device profile and operation
    implementation.

------------------------------------------------------------------------

# Future Enhancements

Potential future improvements include:

## Authentication

Add application login with role-based access.

``` text
Admin
Operator
Viewer
```

## Audit Logging

Record:

``` text
User
Execution ID
Timestamp
Operation
Site
Category
Devices
Result
```

## Scheduling

Allow:

``` text
Daily Pre-Check
Weekly Backup
Scheduled Post-Check
```

## Dashboard

Add:

``` text
Total Devices
Healthy Devices
Failed Devices
Recent Executions
Recent Backups
```

## Notifications

Potential integrations:

``` text
Email
Microsoft Teams
Slack
ServiceNow
```

## Persistent Database

Store execution history in a database instead of relying only on
runtime/report files.

## Job Queue

Long-running automation could be handled through a background job
architecture.

## Multi-user Support

A future enterprise version could support multiple operators executing
jobs simultaneously with role-based access and locking.

------------------------------------------------------------------------

# Quick Start

For an operator who already has the project configured:

## Option 1 --- One Click

Double-click:

``` text
START_NETOPS.bat
```

The application will:

``` text
Start Flask
   ↓
Wait for port 5000
   ↓
Open browser
   ↓
Load NetOps Automation Suite
```

## Option 2 --- PowerShell

``` powershell
cd C:\Users\Prajwal\Documents\Projects\NetOpsAutomationSuite
.\.venv\Scripts\Activate.ps1
python web/app.py
```

Then open:

``` text
http://127.0.0.1:5000
```

------------------------------------------------------------------------

# Typical Operator Workflow

A complete Pre-Check example:

``` text
1. Connect to corporate VPN
          |
          v
2. Start START_NETOPS.bat
          |
          v
3. Browser opens automatically
          |
          v
4. Select PRE-CHECK
          |
          v
5. Select LAB
          |
          v
6. Select Router
          |
          v
7. Review device preview
          |
          v
8. Click RUN PRE-CHECK
          |
          v
9. Confirm execution
          |
          v
10. Automation connects to devices
          |
          v
11. Review execution result
          |
          +--------------------+
          |                    |
          v                    v
       SUCCESS              FAILED
                               |
                               v
                       COPY FAILED
                               |
                               v
                       RETRY FAILED
                               |
                               v
                         Final Result
```

------------------------------------------------------------------------

# Example Final Execution Result

``` text
NetOps Automation Suite

Site        : LAB
Operation   : PRECHECK
Category    : Router
Execution ID: EXEC-20260817-154618

Total Devices : 10
Successful    : 9
Failed        : 1

Device Status
----------------------------------------
R1       10.161.44.200    SUCCESS
R2       10.161.44.201    SUCCESS
CORE     10.161.44.202    FAILED
LAN      10.161.44.203    SUCCESS
```

The operator can then:

``` text
Copy Results
```

or:

``` text
Copy Failed
```

and share the information.

------------------------------------------------------------------------

# Project Design Principles

The suite follows several important design principles.

## Separation of Responsibilities

Inventory should load inventory.

Filters should filter devices.

Operations should define operation workflows.

Executor should execute commands.

Flask should provide the web/API layer.

JavaScript should manage the browser interface.

This makes the project easier to maintain and extend.

## Reusability

Common execution logic should not be duplicated across:

``` text
Precheck
Postcheck
Backup
Retry
```

Instead, common logic should be handled by shared components.

## Least Scope Execution

Only devices matching the selected scope should be executed.

Retry should operate only on failed devices.

## Operator Visibility

The UI should always make it clear:

``` text
What operation is running?
Which site?
Which category?
Which devices?
What succeeded?
What failed?
Which devices are being retried?
```

------------------------------------------------------------------------

# Troubleshooting Checklist

When an execution fails, check in this order:

``` text
[ ] VPN connected
[ ] Correct site selected
[ ] Correct category selected
[ ] Device IP correct
[ ] Device preview correct
[ ] Device reachable
[ ] SSH port reachable
[ ] Credentials valid
[ ] Correct device profile
[ ] Flask terminal logs
[ ] Execution result
[ ] Retry result
```

------------------------------------------------------------------------

# Final Project Status

The current NetOps Automation Suite includes:

``` text
┌──────────────────────────────────────────────┐
│        NETOPS AUTOMATION SUITE               │
├──────────────────────────────────────────────┤
│                                              │
│  ✓ Pre-Check                                │
│  ✓ Post-Check                               │
│  ✓ Backup                                   │
│                                              │
│  ✓ Site Selection                            │
│  ✓ Category Selection                        │
│  ✓ Device Preview                            │
│  ✓ Execution ID                              │
│  ✓ Device-Level Results                      │
│  ✓ Search                                    │
│  ✓ Result Filters                            │
│                                              │
│  ✓ Copy Results                              │
│  ✓ Copy Failed Devices                       │
│                                              │
│  ✓ Retry Failed Devices                      │
│  ✓ Retry Only Failed Devices                 │
│  ✓ Retry Attempt Tracking                    │
│  ✓ Maximum 3 Retry Attempts                  │
│  ✓ Final Success/Failure Calculation         │
│                                              │
│  ✓ Flask Web Application                     │
│  ✓ One-Click BAT Launcher                    │
│                                              │
└──────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# Conclusion

NetOps Automation Suite provides a structured way to automate repetitive
network operations while keeping the operator in control of the
execution scope.

The application combines:

``` text
Python
+
Flask
+
Netmiko
+
Inventory Management
+
Device Filtering
+
Operation Workflows
+
Retry Handling
+
Execution Reporting
+
Web UI
```

The intended operational model is:

``` text
SELECT
   ↓
PREVIEW
   ↓
CONFIRM
   ↓
EXECUTE
   ↓
REVIEW
   ↓
RETRY FAILED (if required)
   ↓
SHARE RESULT
```

For day-to-day use, the recommended starting point is simply:

``` text
Double-click START_NETOPS.bat
```

and allow the launcher to start Flask and open the local application
automatically.

------------------------------------------------------------------------

## Maintainer Notes

When making future changes:

-   Preserve separation between UI and automation logic.
-   Avoid hardcoding credentials.
-   Test against lab devices before production devices.
-   Test both successful and failed execution paths.
-   Test retry behavior after executor changes.
-   Keep `requirements.txt` synchronized intentionally.
-   Update this README when major architecture or workflow changes are
    introduced.
