"""
===============================================================================
File Name   : menu.py
Project     : NetOps Automation Suite
Description : Interactive CLI Menu
===============================================================================

Purpose
-------
This module handles the user's menu selections.

Version 1.0 supports ONLY:

1. Precheck
2. Postcheck
3. Backup
4. Exit

The menu dynamically reads:

- Sites
- Categories

from the loaded inventory.

Nothing is hardcoded.

===============================================================================
"""

# Questionary provides arrow-key menus.
import questionary

# Rich provides clean terminal formatting.
from rich.console import Console
from rich.panel import Panel

# Import Device type for type hints.
from models.device import Device

# Inventory provides dynamic site/category information.
from core.inventory import Inventory


# Create one Rich Console object for terminal output.
console = Console()


class Menu:
    """
    Handles all interactive menus for NetOps Automation Suite.
    """

    # -------------------------------------------------------------------------
    # Application Header
    # -------------------------------------------------------------------------

    @staticmethod
    def show_header() -> None:
        """
        Display the application title.
        """

        console.print()

        console.print(
            Panel.fit(
                "[bold]NetOps Automation Suite[/bold]\n"
                "[dim]Precheck | Postcheck | Backup[/dim]",
                title="Version 1.0",
            )
        )

        console.print()

    # -------------------------------------------------------------------------
    # Operation Selection
    # -------------------------------------------------------------------------

    @staticmethod
    def select_operation() -> str:
        """
        Ask the user which operation should be performed.

        Version 1.0 operations:

        Precheck
        Postcheck
        Backup
        Exit

        Returns
        -------
        str
            Selected operation.
        """

        operation = questionary.select(
            "Select Operation:",
            choices=[
                "Precheck",
                "Postcheck",
                "Backup",
                "Exit",
            ],
        ).ask()

        # Ctrl+C / Ctrl+Z may cause Questionary to return None.
        if operation is None:
            return "Exit"

        return operation

    # -------------------------------------------------------------------------
    # Site Selection
    # -------------------------------------------------------------------------

    @staticmethod
    def select_site(
        devices: list[Device],
    ) -> str:
        """
        Dynamically display sites from Excel.

        Example inventory sites:

        AA
        AB
        AC

        Menu:

        All Sites
        AA
        AB
        AC

        Returns
        -------
        str
            "All" or the actual selected site.
        """

        # Dynamically retrieve site names from inventory.
        sites = Inventory.get_unique_values(
            devices,
            "site"
        )

        # Stop if no sites exist.
        if not sites:
            raise ValueError(
                "No active sites were found in the inventory."
            )

        # Display-friendly menu.
        choices = ["All Sites"] + sites

        selected_site = questionary.select(
            "Select Site:",
            choices=choices,
        ).ask()

        # Treat cancelled menu as application exit/cancel.
        if selected_site is None:
            return "All"

        # Filters internally understand "All".
        if selected_site == "All Sites":
            return "All"

        # Otherwise return the real Excel site name.
        return selected_site

    # -------------------------------------------------------------------------
    # Category Selection
    # -------------------------------------------------------------------------

    @staticmethod
    def select_category(
        devices: list[Device],
    ) -> str:
        """
        Dynamically display device categories.

        Example inventory:

        Router
        Switch
        Wireless

        Menu:

        All Devices
        Router
        Switch
        Wireless

        Returns
        -------
        str
            "All" or selected category.
        """

        # Get categories dynamically from active inventory.
        categories = Inventory.get_unique_values(
            devices,
            "category"
        )

        # Stop if no categories exist.
        if not categories:
            raise ValueError(
                "No device categories were found in the inventory."
            )

        # Add our special All Devices option.
        choices = ["All Devices"] + categories

        selected_category = questionary.select(
            "Select Device Category:",
            choices=choices,
        ).ask()

        if selected_category is None:
            return "All"

        # Convert display value into our internal filter value.
        if selected_category == "All Devices":
            return "All"

        return selected_category

    # -------------------------------------------------------------------------
    # Confirmation Screen
    # -------------------------------------------------------------------------

    @staticmethod
    def confirm_execution(
        operation: str,
        site: str,
        category: str,
        device_count: int,
    ) -> bool:
        """
        Show the final scope before execution.

        This is important because later this tool will connect to
        production network devices.

        Example:

        Operation : Precheck
        Site      : AB
        Category  : Router
        Devices   : 25

        Proceed?
        """

        # Convert internal "All" values into user-friendly text.
        site_display = (
            "All Sites"
            if site == "All"
            else site
        )

        category_display = (
            "All Devices"
            if category == "All"
            else category
        )

        # Display execution summary.
        console.print()

        console.print(
            Panel(
                f"[bold]Operation:[/bold] {operation}\n"
                f"[bold]Site:[/bold] {site_display}\n"
                f"[bold]Category:[/bold] {category_display}\n"
                f"[bold]Devices Found:[/bold] {device_count}",
                title="Execution Summary",
            )
        )

        console.print()

        # Prevent execution if the filter returned zero devices.
        if device_count == 0:
            console.print(
                "[bold red]No devices matched the selected scope.[/bold red]"
            )

            return False

        # Ask for final confirmation.
        confirmation = questionary.confirm(
            "Proceed with this operation?",
            default=False,
        ).ask()

        # Cancelled prompt = don't proceed.
        if confirmation is None:
            return False

        return confirmation

    # -------------------------------------------------------------------------
    # Exit Message
    # -------------------------------------------------------------------------

    @staticmethod
    def show_exit_message() -> None:
        """
        Display application exit message.
        """

        console.print()

        console.print(
            "[bold]NetOps Automation Suite closed.[/bold]"
        )

        console.print()