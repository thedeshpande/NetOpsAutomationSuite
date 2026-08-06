"""
===============================================================================
File Name   : device.py
Project     : NetOps Automation Suite
Description : Network Device Data Model
===============================================================================

Purpose
-------
This module defines the Device object used throughout the application.

Every ACTIVE row from inventory/devices.xlsx will be converted into
one Device object.

Example
-------
An Excel row:

Active | AB | RTR01 | 10.10.10.1 | Router | IOS_ROUTER | ISR4331 ...

becomes:

Device(
    status="Active",
    site="AB",
    hostname="RTR01",
    management_ip="10.10.10.1",
    ...
)

===============================================================================
"""

# dataclass automatically creates the constructor and other useful methods.
from dataclasses import dataclass


@dataclass
class Device:
    """
    Represents one network device from the Excel inventory.

    Attributes
    ----------
    status:
        Device inventory status. Only "Active" devices are loaded.

    site:
        Site/location name.

    hostname:
        Network device hostname.

    management_ip:
        IP address used by Netmiko for SSH connectivity.

    category:
        High-level device category.
        Example: Router, Switch, Wireless.

    profile:
        Automation profile used to determine commands and SSH behaviour.
        Example: IOS_ROUTER, IOS_SWITCH, CEDGE, VEDGE, AIREOS.

    platform:
        Hardware platform/model.
        Example: ISR4331, C9300, C8500.

    os:
        Operating system.
        Example: IOS, IOS-XE, SDWAN, AireOS.

    vendor:
        Device vendor.
        Example: Cisco.

    credential_profile:
        Credential profile name that will later be used for authentication.
        Example: TACACS.
    """

    # Inventory status.
    status: str

    # Site/location of the device.
    site: str

    # Device hostname.
    hostname: str

    # SSH management IP address.
    management_ip: str

    # Router / Switch / Wireless etc.
    category: str

    # IOS_ROUTER / CEDGE / VEDGE / AIREOS etc.
    profile: str

    # Hardware platform/model.
    platform: str

    # Device operating system.
    os: str

    # Vendor name.
    vendor: str

    # Credential profile reference.
    credential_profile: str