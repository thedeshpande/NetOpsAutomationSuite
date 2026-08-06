"""
===============================================================================
File Name   : filters.py
Project     : NetOps Automation Suite
Description : Device Filtering Engine
===============================================================================

Purpose
-------
This module filters Device objects.

Examples:

All devices at site AB

AB + Router

AC + Wireless

All Sites + Router

All Sites + All Devices

This module DOES NOT:

- Read Excel
- Connect through SSH
- Execute commands
- Perform Precheck
- Perform Postcheck
- Perform Backup

===============================================================================
"""

# Import our Device object.
from models.device import Device


class DeviceFilter:
    """
    Provides reusable filtering functions for network devices.
    """

    # -------------------------------------------------------------------------
    # Filter by Site
    # -------------------------------------------------------------------------

    @staticmethod
    def by_site(
        devices: list[Device],
        site: str,
    ) -> list[Device]:
        """
        Filter devices by site.

        If site is "All", every device is returned.

        Example
        -------
        DeviceFilter.by_site(devices, "AB")
        """

        # "All" means don't apply a site filter.
        if site.strip().casefold() == "all":
            return list(devices)

        # Return only devices matching the selected site.
        return [
            device
            for device in devices
            if device.site.strip().casefold()
            == site.strip().casefold()
        ]

    # -------------------------------------------------------------------------
    # Filter by Category
    # -------------------------------------------------------------------------

    @staticmethod
    def by_category(
        devices: list[Device],
        category: str,
    ) -> list[Device]:
        """
        Filter devices by category.

        Examples:

        Router
        Switch
        Wireless

        IMPORTANT
        ---------
        Category and Profile are different.

        Example:

        Category = Router

        Profiles could be:

        IOS_ROUTER
        CEDGE
        VEDGE

        Therefore selecting Router automatically includes all Router profiles.
        """

        # "All" means don't apply a category filter.
        if category.strip().casefold() == "all":
            return list(devices)

        # Return every device belonging to the selected category.
        return [
            device
            for device in devices
            if device.category.strip().casefold()
            == category.strip().casefold()
        ]

    # -------------------------------------------------------------------------
    # Filter by Profile
    # -------------------------------------------------------------------------

    @staticmethod
    def by_profile(
        devices: list[Device],
        profile: str,
    ) -> list[Device]:
        """
        Filter devices by automation profile.

        Example profiles:

        IOS_ROUTER
        IOS_SWITCH
        CEDGE
        VEDGE
        AIREOS
        """

        if profile.strip().casefold() == "all":
            return list(devices)

        return [
            device
            for device in devices
            if device.profile.strip().casefold()
            == profile.strip().casefold()
        ]

    # -------------------------------------------------------------------------
    # Filter by Vendor
    # -------------------------------------------------------------------------

    @staticmethod
    def by_vendor(
        devices: list[Device],
        vendor: str,
    ) -> list[Device]:
        """
        Filter devices by vendor.

        Example:

        Cisco
        Aruba
        """

        if vendor.strip().casefold() == "all":
            return list(devices)

        return [
            device
            for device in devices
            if device.vendor.strip().casefold()
            == vendor.strip().casefold()
        ]

    # -------------------------------------------------------------------------
    # Search by Hostname
    # -------------------------------------------------------------------------

    @staticmethod
    def by_hostname(
        devices: list[Device],
        hostname: str,
    ) -> list[Device]:
        """
        Search devices using a hostname or partial hostname.

        Example:

        Search:
            RTR

        Could return:
            AB-RTR01
            AB-RTR02
            AC-RTR01
        """

        # Normalize the search text.
        search_text = hostname.strip().casefold()

        # Empty search returns every device.
        if not search_text:
            return list(devices)

        return [
            device
            for device in devices
            if search_text in device.hostname.casefold()
        ]

    # -------------------------------------------------------------------------
    # Apply Site + Category
    # -------------------------------------------------------------------------

    @staticmethod
    def apply(
        devices: list[Device],
        site: str = "All",
        category: str = "All",
    ) -> list[Device]:
        """
        Apply the filters used by our Version 1.0 workflow.

        The user selects:

        Site
            +
        Category

        Examples
        --------

        AB + Router

        AB + All

        All + Wireless

        All + All

        Returns
        -------
        list[Device]
            Devices matching the requested scope.
        """

        # First filter by site.
        filtered_devices = DeviceFilter.by_site(
            devices,
            site
        )

        # Then filter that result by category.
        filtered_devices = DeviceFilter.by_category(
            filtered_devices,
            category
        )

        # Sort the final list by hostname.
        return DeviceFilter.sort_by_hostname(
            filtered_devices
        )

    # -------------------------------------------------------------------------
    # Sort Devices
    # -------------------------------------------------------------------------

    @staticmethod
    def sort_by_hostname(
        devices: list[Device],
    ) -> list[Device]:
        """
        Sort devices alphabetically by hostname.
        """

        return sorted(
            devices,
            key=lambda device: device.hostname.casefold()
        )

    # -------------------------------------------------------------------------
    # Device Count
    # -------------------------------------------------------------------------

    @staticmethod
    def count(devices: list[Device]) -> int:
        """
        Return number of devices in a list.
        """

        return len(devices)