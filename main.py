"""
main.py
-------
Entry point for NetOps Automation Suite.
"""

from core.inventory import Inventory
from core.filters import DeviceFilter
from core.menu import Menu
from core.executor import Executor

from operations.precheck import PrecheckOperation
from operations.postcheck import PostcheckOperation
from operations.backup import BackupOperation


def main():
    """Application entry point."""

    Menu.show_header()

    try:

        # ==============================================================
        # LOAD INVENTORY
        # ==============================================================

        devices = Inventory.load_devices()

        if not devices:

            print("No active devices found.")

            return

        # ==============================================================
        # USER SELECTIONS
        # ==============================================================

        operation = Menu.select_operation()

        if operation == "Exit":

            Menu.show_exit_message()

            return

        site = Menu.select_site(
            devices
        )

        category = Menu.select_category(
            devices
        )

        # ==============================================================
        # FILTER DEVICES
        # ==============================================================

        filtered_devices = DeviceFilter.apply(
            devices=devices,
            site=site,
            category=category,
        )

        # ==============================================================
        # GENERATE EXECUTION ID
        # ==============================================================

        execution_id = (
            Executor.generate_execution_id()
        )

        # ==============================================================
        # PRE-EXECUTION REVIEW
        # ==============================================================

        confirmed = Menu.confirm_execution(
            operation=operation,
            site=site,
            category=category,
            devices=filtered_devices,
            execution_id=execution_id,
        )

        # ==============================================================
        # USER CANCELLED
        # ==============================================================

        if not confirmed:

            print("\nOperation cancelled.")

            return

        # ==============================================================
        # EXECUTE SELECTED OPERATION
        # ==============================================================

        if operation == "Precheck":

            PrecheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )

        elif operation == "Postcheck":

            PostcheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )

        elif operation == "Backup":

            BackupOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )

        # ==============================================================
        # COMPLETION MESSAGE
        # ==============================================================

        print("\n")
        print("=" * 80)
        print("AUTOMATION COMPLETED SUCCESSFULLY")
        print("=" * 80)
        print(
            f"Execution ID : {execution_id}"
        )
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