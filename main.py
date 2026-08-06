"""
main.py
-------
Entry point for NetOps Automation Suite.
"""

from core.inventory import Inventory
from core.filters import DeviceFilter
from core.menu import Menu

from operations.precheck import PrecheckOperation
from operations.postcheck import PostcheckOperation
from operations.backup import BackupOperation


def main():
    """Application entry point."""

    Menu.show_header()

    try:
        # Load inventory
        devices = Inventory.load_devices()

        if not devices:
            print("No active devices found.")
            return

        # User selections
        operation = Menu.select_operation()

        if operation == "Exit":
            Menu.show_exit_message()
            return

        site = Menu.select_site(devices)

        category = Menu.select_category(devices)

        # Filter devices
        filtered_devices = DeviceFilter.apply(
            devices=devices,
            site=site,
            category=category,
        )

        # Confirmation
        confirmed = Menu.confirm_execution(
            operation=operation,
            site=site,
            category=category,
            device_count=len(filtered_devices),
        )

        if not confirmed:
            print("\nOperation cancelled.")
            return

        # Execute selected operation
        if operation == "Precheck":

            PrecheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
            )

        elif operation == "Postcheck":

            PostcheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
            )

        elif operation == "Backup":

            BackupOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
            )

        print("\n")
        print("=" * 80)
        print("Automation Completed Successfully")
        print("=" * 80)

    except Exception as error:

        print("\n")
        print("=" * 80)
        print("APPLICATION ERROR")
        print("=" * 80)
        print(error)
        print("=" * 80)


if __name__ == "__main__":
    main()