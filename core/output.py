"""
output.py
---------
"""

from datetime import datetime
from pathlib import Path

from models.device import Device


class OutputManager:
    """Handles all output folder and file operations."""

    @staticmethod
    def get_output_root() -> Path:
        """
        Returns the project output directory.
        """

        project_root = Path(__file__).resolve().parent.parent

        output_root = project_root / "output"

        output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return output_root

    @staticmethod
    def get_date_folder() -> str:
        """
        Returns today's date.

        Example
        -------
        2026-08-07
        """

        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def get_operation_folder(operation: str) -> str:
        """
        Converts operation name into folder name.
        """

        mapping = {
            "precheck": "Precheck",
            "postcheck": "Postcheck",
            "backup": "Backup",
        }

        return mapping.get(
            operation.lower(),
            operation.capitalize(),
        )

    @staticmethod
    def create_output_folder(
        device: Device,
        operation: str,
    ) -> Path:
        """
        Creates output folder.

        Example

        output/
            AB/
                2026-08-07/
                    RTR01/
                        Precheck/
        """

        folder = (
            OutputManager.get_output_root()
            / device.site
            / OutputManager.get_date_folder()
            / device.hostname
            / OutputManager.get_operation_folder(operation)
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    @staticmethod
    def save_output(
        device: Device,
        operation: str,
        command_outputs: dict,
    ) -> Path:
        """
        Save command outputs into a timestamped file.

        Returns
        -------
        Path
            Full path of the saved output file.
        """

        output_folder = OutputManager.create_output_folder(
            device,
            operation,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_file = (
            output_folder
            / f"{operation.lower()}_{timestamp}.txt"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write("=" * 100 + "\n")
            file.write("NetOps Automation Suite\n")
            file.write("=" * 100 + "\n\n")

            file.write(f"Hostname   : {device.hostname}\n")
            file.write(f"IP Address : {device.management_ip}\n")
            file.write(f"Site       : {device.site}\n")
            file.write(f"Category   : {device.category}\n")
            file.write(f"Profile    : {device.profile}\n")
            file.write(f"Platform   : {device.platform}\n")
            file.write(f"OS         : {device.os}\n")
            file.write(f"Vendor     : {device.vendor}\n")
            file.write(f"Operation  : {operation.capitalize()}\n")
            file.write(
                f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")
            file.write("=" * 100)
            file.write("\n\n")

            for command, output in command_outputs.items():

                file.write("#" * 100)
                file.write("\n")

                file.write(f"COMMAND : {command}\n")

                file.write("#" * 100)
                file.write("\n\n")

                file.write(output.rstrip())

                file.write("\n\n")

        return output_file

    @staticmethod
    def save_failed_output(
        device: Device,
        operation: str,
        error: str,
    ) -> Path:
        """
        Save connection/authentication failures.
        """

        output_folder = OutputManager.create_output_folder(
            device,
            operation,
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        output_file = (
            output_folder
            / f"{operation.lower()}_{timestamp}_FAILED.txt"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write("=" * 100 + "\n")
            file.write("NetOps Automation Suite\n")
            file.write("DEVICE EXECUTION FAILED\n")
            file.write("=" * 100 + "\n\n")

            file.write(f"Hostname   : {device.hostname}\n")
            file.write(f"IP Address : {device.management_ip}\n")
            file.write(f"Site       : {device.site}\n")
            file.write(f"Operation  : {operation.capitalize()}\n")
            file.write(
                f"Generated  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")
            file.write("-" * 100)
            file.write("\n\n")

            file.write("ERROR\n")
            file.write("-----\n")
            file.write(error)

        return output_file