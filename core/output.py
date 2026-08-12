"""
output.py
---------
Handles all output folder and file operations
for NetOps Automation Suite.
"""

from datetime import datetime
from pathlib import Path

from models.device import Device


class OutputManager:
    """Handles all output folder and file operations."""

    # =========================================================================
    # OUTPUT ROOT
    # =========================================================================

    @staticmethod
    def get_output_root() -> Path:
        """
        Returns the project output directory.

        Example
        -------
        NetOpsAutomationSuite/
            output/
        """

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        output_root = (
            project_root / "output"
        )

        output_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return output_root

    # =========================================================================
    # DATE FOLDER
    # =========================================================================

    @staticmethod
    def get_date_folder() -> str:
        """
        Returns today's date.

        Example
        -------
        2026-08-13
        """

        return datetime.now().strftime(
            "%Y-%m-%d"
        )

    # =========================================================================
    # OPERATION FOLDER
    # =========================================================================

    @staticmethod
    def get_operation_folder(
        operation: str,
    ) -> str:
        """
        Converts operation name into folder name.

        Supported operations
        --------------------
        precheck
        postcheck
        backup
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

    # =========================================================================
    # CREATE OUTPUT FOLDER
    # =========================================================================

    @staticmethod
    def create_output_folder(
        device: Device,
        operation: str,
    ) -> Path:
        """
        Creates the device output folder.

        Example
        -------

        output/
            AB/
                2026-08-13/
                    R1/
                        Precheck/
                        Postcheck/
                        Backup/
        """

        folder = (
            OutputManager.get_output_root()
            / device.site
            / OutputManager.get_date_folder()
            / device.hostname
            / OutputManager.get_operation_folder(
                operation
            )
        )

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder

    # =========================================================================
    # OUTPUT FILENAME
    # =========================================================================

    @staticmethod
    def get_output_filename(
        device: Device,
        operation: str,
        execution_id: str = "",
        failed: bool = False,
    ) -> str:
        """
        Generate a clear and unique output filename.

        Format
        ------

        Hostname_IPAddress_ExecutionID_Date_Time.txt

        Example
        -------

        R1_192.168.122.1_EXEC-20260813-214530_20260813_214535.txt

        Failed Example
        --------------

        R1_192.168.122.1_EXEC-20260813-214530_20260813_214540_FAILED.txt
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        hostname = str(
            device.hostname
        ).strip()

        ip_address = str(
            device.management_ip
        ).strip()

        # ---------------------------------------------------------------------
        # Base filename
        # ---------------------------------------------------------------------

        filename = (
            f"{hostname}_"
            f"{ip_address}_"
        )

        # ---------------------------------------------------------------------
        # Add Execution ID when available
        # ---------------------------------------------------------------------

        if execution_id:

            filename += (
                f"{execution_id}_"
            )

        # ---------------------------------------------------------------------
        # Timestamp
        # ---------------------------------------------------------------------

        filename += timestamp

        # ---------------------------------------------------------------------
        # Failed marker
        # ---------------------------------------------------------------------

        if failed:

            filename += "_FAILED"

        filename += ".txt"

        return filename

    # =========================================================================
    # SAVE SUCCESSFUL OUTPUT
    # =========================================================================

    @staticmethod
    def save_output(
        device: Device,
        operation: str,
        command_outputs: dict,
        execution_id: str = "",
    ) -> Path:
        """
        Save successful command outputs.

        Parameters
        ----------
        device
            Device object.

        operation
            precheck / postcheck / backup.

        command_outputs
            Dictionary containing command and output.

        execution_id
            Unique ID for the current automation run.

        Example
        -------

        R1_192.168.122.1_EXEC-20260813-214530_20260813_214535.txt
        """

        output_folder = (
            OutputManager.create_output_folder(
                device=device,
                operation=operation,
            )
        )

        output_file = (
            output_folder
            / OutputManager.get_output_filename(
                device=device,
                operation=operation,
                execution_id=execution_id,
                failed=False,
            )
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            # ==============================================================
            # HEADER
            # ==============================================================

            file.write(
                "=" * 100 + "\n"
            )

            file.write(
                "NetOps Automation Suite\n"
            )

            file.write(
                "=" * 100 + "\n\n"
            )

            # ==============================================================
            # EXECUTION INFORMATION
            # ==============================================================

            file.write(
                f"Execution ID : "
                f"{execution_id}\n"
            )

            file.write(
                f"Hostname     : "
                f"{device.hostname}\n"
            )

            file.write(
                f"IP Address   : "
                f"{device.management_ip}\n"
            )

            file.write(
                f"Site         : "
                f"{device.site}\n"
            )

            file.write(
                f"Category     : "
                f"{device.category}\n"
            )

            file.write(
                f"Profile      : "
                f"{device.profile}\n"
            )

            file.write(
                f"Platform     : "
                f"{device.platform}\n"
            )

            file.write(
                f"OS           : "
                f"{device.os}\n"
            )

            file.write(
                f"Vendor       : "
                f"{device.vendor}\n"
            )

            file.write(
                f"Operation    : "
                f"{operation.capitalize()}\n"
            )

            file.write(
                f"Generated    : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")

            file.write(
                "=" * 100 + "\n\n"
            )

            # ==============================================================
            # COMMAND OUTPUTS
            # ==============================================================

            for command, output in (
                command_outputs.items()
            ):

                file.write(
                    "#" * 100 + "\n"
                )

                file.write(
                    f"COMMAND : {command}\n"
                )

                file.write(
                    "#" * 100 + "\n\n"
                )

                file.write(
                    output.rstrip()
                )

                file.write(
                    "\n\n"
                )

        return output_file

    # =========================================================================
    # SAVE FAILED OUTPUT
    # =========================================================================

    @staticmethod
    def save_failed_output(
        device: Device,
        operation: str,
        error: str,
        execution_id: str = "",
    ) -> Path:
        """
        Save connection/authentication/execution failures.

        Example
        -------

        R1_192.168.122.1_EXEC-20260813-214530_20260813_214540_FAILED.txt
        """

        output_folder = (
            OutputManager.create_output_folder(
                device=device,
                operation=operation,
            )
        )

        output_file = (
            output_folder
            / OutputManager.get_output_filename(
                device=device,
                operation=operation,
                execution_id=execution_id,
                failed=True,
            )
        )

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as file:

            # ==============================================================
            # HEADER
            # ==============================================================

            file.write(
                "=" * 100 + "\n"
            )

            file.write(
                "NetOps Automation Suite\n"
            )

            file.write(
                "DEVICE EXECUTION FAILED\n"
            )

            file.write(
                "=" * 100 + "\n\n"
            )

            # ==============================================================
            # EXECUTION INFORMATION
            # ==============================================================

            file.write(
                f"Execution ID : "
                f"{execution_id}\n"
            )

            file.write(
                f"Hostname     : "
                f"{device.hostname}\n"
            )

            file.write(
                f"IP Address   : "
                f"{device.management_ip}\n"
            )

            file.write(
                f"Site         : "
                f"{device.site}\n"
            )

            file.write(
                f"Category     : "
                f"{device.category}\n"
            )

            file.write(
                f"Profile      : "
                f"{device.profile}\n"
            )

            file.write(
                f"Operation    : "
                f"{operation.capitalize()}\n"
            )

            file.write(
                f"Generated    : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")

            file.write(
                "-" * 100 + "\n\n"
            )

            # ==============================================================
            # ERROR
            # ==============================================================

            file.write(
                "ERROR\n"
            )

            file.write(
                "-----\n"
            )

            file.write(
                error
            )

            file.write(
                "\n"
            )

        return output_file