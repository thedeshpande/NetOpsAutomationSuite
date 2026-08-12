"""
===============================================================================
File Name   : menu.py
Project     : NetOps Automation Suite
Description : Interactive CLI Menu
===============================================================================

Purpose
-------
Handles all interactive menus and pre-execution validation.

Supported Operations:

1. Precheck
2. Postcheck
3. Backup
4. Exit

The menu dynamically reads:

- Sites
- Categories

from the loaded inventory.

Before execution, the tool displays:

- Execution ID
- Operation
- Site
- Category
- Device count
- Command count
- Exact devices selected

The user must explicitly confirm the execution.

===============================================================================
"""

import questionary

from rich.console import Console
from rich.panel import Panel

from models.device import Device

from core.inventory import Inventory
from core.profiles import ProfileManager


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
        Dynamically display sites from inventory.
        """

        sites = Inventory.get_unique_values(
            devices,
            "site",
        )

        if not sites:

            raise ValueError(
                "No active sites were found in the inventory."
            )

        choices = [
            "All Sites"
        ] + sites

        selected_site = questionary.select(
            "Select Site:",
            choices=choices,
        ).ask()

        if selected_site is None:

            return "All"

        if selected_site == "All Sites":

            return "All"

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
        """

        categories = Inventory.get_unique_values(
            devices,
            "category",
        )

        if not categories:

            raise ValueError(
                "No device categories were found in the inventory."
            )

        choices = [
            "All Devices"
        ] + categories

        selected_category = questionary.select(
            "Select Device Category:",
            choices=choices,
        ).ask()

        if selected_category is None:

            return "All"

        if selected_category == "All Devices":

            return "All"

        return selected_category

    # -------------------------------------------------------------------------
    # Build Execution Plan
    # -------------------------------------------------------------------------

    @staticmethod
    def build_execution_plan(
        devices: list[Device],
        operation: str,
    ) -> dict:
        """
        Validate profiles and calculate the number of commands
        that will be executed.

        Returns
        -------
        dict
            Execution planning information.
        """

        total_commands = 0

        profile_errors = []

        device_command_counts = {}

        for device in devices:

            try:

                # Validate profile
                ProfileManager.load_profile(
                    device.profile
                )

                # Load operation commands
                commands = (
                    ProfileManager.load_commands(
                        device.profile,
                        operation.lower(),
                    )
                )

                command_count = len(
                    commands
                )

                total_commands += command_count

                device_command_counts[
                    device.hostname
                ] = command_count

            except Exception as error:

                profile_errors.append(
                    {
                        "hostname": device.hostname,
                        "ip": device.management_ip,
                        "profile": device.profile,
                        "error": str(error),
                    }
                )

        return {
            "device_count": len(devices),
            "command_count": total_commands,
            "device_command_counts": device_command_counts,
            "profile_errors": profile_errors,
        }

    # -------------------------------------------------------------------------
    # Confirmation Screen
    # -------------------------------------------------------------------------

    @staticmethod
    def confirm_execution(
        operation: str,
        site: str,
        category: str,
        devices: list[Device],
        execution_id: str,
    ) -> bool:
        """
        Display the complete pre-execution review.

        No SSH connection is performed here.

        The user must explicitly confirm the displayed scope.
        """

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

        # ==============================================================
        # BUILD EXECUTION PLAN
        # ==============================================================

        plan = Menu.build_execution_plan(
            devices=devices,
            operation=operation,
        )

        device_count = plan[
            "device_count"
        ]

        command_count = plan[
            "command_count"
        ]

        profile_errors = plan[
            "profile_errors"
        ]

        # ==============================================================
        # HEADER
        # ==============================================================

        console.print()

        console.print(
            Panel(
                f"[bold cyan]Execution ID:[/bold cyan] "
                f"{execution_id}\n"
                f"[bold]Operation:[/bold] "
                f"{operation.upper()}\n"
                f"[bold]Site:[/bold] "
                f"{site_display}\n"
                f"[bold]Category:[/bold] "
                f"{category_display}\n"
                f"[bold]Devices Found:[/bold] "
                f"{device_count}\n"
                f"[bold]Commands:[/bold] "
                f"{command_count}",
                title="PRE-EXECUTION REVIEW",
                border_style="cyan",
            )
        )

        # ==============================================================
        # ZERO DEVICES
        # ==============================================================

        if device_count == 0:

            console.print()

            console.print(
                "[bold red]"
                "No devices matched the selected scope."
                "[/bold red]"
            )

            return False

        # ==============================================================
        # PROFILE VALIDATION ERRORS
        # ==============================================================

        if profile_errors:

            console.print()

            console.print(
                Panel(
                    "[bold red]"
                    "Pre-execution validation failed."
                    "[/bold red]\n\n"
                    "The following devices have profile or "
                    "command configuration issues:",
                    title="VALIDATION ERROR",
                    border_style="red",
                )
            )

            console.print()

            for error in profile_errors:

                console.print(
                    f"[red]✖[/red] "
                    f"{error['hostname']} "
                    f"({error['ip']})"
                )

                console.print(
                    f"   Profile : "
                    f"{error['profile']}"
                )

                console.print(
                    f"   Reason  : "
                    f"{error['error']}"
                )

            console.print()

            console.print(
                "[bold red]"
                "Execution blocked."
                "[/bold red]"
            )

            return False

        # ==============================================================
        # DEVICE LIST
        # ==============================================================

        console.print()

        console.print(
            Panel(
                "",
                title="SELECTED DEVICES",
                border_style="blue",
            )
        )

        console.print(
            f"{'Hostname':<25}"
            f"{'IP Address':<20}"
            f"{'Profile':<20}"
            f"Commands"
        )

        console.print(
            "-" * 85
        )

        for device in devices:

            command_count_for_device = (
                plan[
                    "device_command_counts"
                ].get(
                    device.hostname,
                    0,
                )
            )

            console.print(
                f"{device.hostname:<25}"
                f"{device.management_ip:<20}"
                f"{device.profile:<20}"
                f"{command_count_for_device}"
            )

        console.print(
            "-" * 85
        )

        # ==============================================================
        # SAFETY MESSAGE
        # ==============================================================

        console.print()

        console.print(
            "[bold yellow]"
            "⚠ Please verify the above scope before execution."
            "[/bold yellow]"
        )

        console.print(
            "[dim]"
            "No device connections have been initiated yet."
            "[/dim]"
        )

        console.print()

        # ==============================================================
        # FINAL CONFIRMATION
        # ==============================================================

        confirmation = questionary.confirm(
            "Proceed with this operation?",
            default=False,
        ).ask()

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