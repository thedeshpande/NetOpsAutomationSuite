"""
reports.py
----------
Generates execution summary reports for NetOps Automation Suite.
"""

from datetime import datetime
from pathlib import Path


class ReportManager:
    """Creates execution summary reports."""

    @staticmethod
    def get_reports_root() -> Path:
        """
        Returns:

        reports/
        """

        project_root = (
            Path(__file__).resolve().parent.parent
        )

        reports_root = (
            project_root / "reports"
        )

        reports_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return reports_root

    @staticmethod
    def get_report_folder() -> Path:
        """
        Returns:

        reports/YYYY-MM-DD/
        """

        report_folder = (
            ReportManager.get_reports_root()
            / datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        report_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return report_folder

    @staticmethod
    def create_report_file(
        operation: str,
        execution_id: str = "",
    ) -> Path:
        """
        Create a timestamped report file.

        Example:

        PRECHECK_Report_EXEC-20260813-214530_20260813_214535.txt
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        if execution_id:

            report_name = (
                f"{operation.upper()}_Report_"
                f"{execution_id}_"
                f"{timestamp}.txt"
            )

        else:

            report_name = (
                f"{operation.upper()}_Report_"
                f"{timestamp}.txt"
            )

        return (
            ReportManager.get_report_folder()
            / report_name
        )

    @staticmethod
    def generate(
        operation: str,
        site: str,
        category: str,
        results: list[dict],
    ) -> Path:
        """
        Generate execution report.
        """

        # ==============================================================
        # EXECUTION ID
        # ==============================================================

        execution_id = ""

        if results:

            execution_id = results[0].get(
                "execution_id",
                "",
            )

        # ==============================================================
        # REPORT FILE
        # ==============================================================

        report_file = (
            ReportManager.create_report_file(
                operation=operation,
                execution_id=execution_id,
            )
        )

        # ==============================================================
        # STATISTICS
        # ==============================================================

        total = len(results)

        success = sum(
            1
            for result in results
            if result.get("status")
            == "SUCCESS"
        )

        failed = sum(
            1
            for result in results
            if result.get("status")
            == "FAILED"
        )

        skipped = sum(
            1
            for result in results
            if result.get("status")
            == "SKIPPED"
        )

        total_commands = sum(
            len(
                result.get(
                    "commands",
                    {},
                )
            )
            for result in results
        )

        # ==============================================================
        # WRITE REPORT
        # ==============================================================

        with open(
            report_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(
                "=" * 100 + "\n"
            )

            file.write(
                "                         NETOPS AUTOMATION SUITE\n"
            )

            file.write(
                "                         EXECUTION REPORT\n"
            )

            file.write(
                "=" * 100 + "\n\n"
            )

            # ----------------------------------------------------------
            # Execution Information
            # ----------------------------------------------------------

            file.write(
                f"Execution ID : {execution_id}\n"
            )

            file.write(
                f"Operation    : {operation.upper()}\n"
            )

            file.write(
                f"Site         : {site}\n"
            )

            file.write(
                f"Category     : {category}\n"
            )

            file.write(
                "Generated    : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")

            file.write(
                "-" * 100 + "\n"
            )

            # ----------------------------------------------------------
            # Device Results
            # ----------------------------------------------------------

            file.write(
                f"{'Hostname':20}"
                f"{'Status':12}"
                f"{'IP Address':18}"
                "Output File\n"
            )

            file.write(
                "-" * 100 + "\n"
            )

            for result in results:

                hostname = result.get(
                    "hostname",
                    "",
                )

                status = result.get(
                    "status",
                    "",
                )

                ip = result.get(
                    "ip",
                    "",
                )

                output_file = result.get(
                    "output_file",
                    "",
                )

                file.write(
                    f"{hostname:20}"
                    f"{status:12}"
                    f"{ip:18}"
                    f"{output_file}\n"
                )

            file.write("\n")

            file.write(
                "=" * 100 + "\n\n"
            )

            # ----------------------------------------------------------
            # Summary
            # ----------------------------------------------------------

            file.write(
                "SUMMARY\n"
            )

            file.write(
                "-" * 100 + "\n"
            )

            executed = (
                success + failed
            )

            success_rate = (
                (success / total) * 100
                if total
                else 0
            )

            file.write(
                f"Total Devices      : {total}\n"
            )

            file.write(
                f"Executed Devices   : {executed}\n"
            )

            file.write(
                f"Successful         : {success}\n"
            )

            file.write(
                f"Failed             : {failed}\n"
            )

            file.write(
                f"Skipped            : {skipped}\n"
            )

            file.write(
                f"Total Commands     : {total_commands}\n"
            )

            file.write(
                f"Success Rate       : "
                f"{success_rate:.1f}%\n"
            )

            # ----------------------------------------------------------
            # Failed Devices
            # ----------------------------------------------------------

            if failed > 0:

                file.write("\n")

                file.write(
                    "FAILED DEVICES\n"
                )

                file.write(
                    "-" * 100 + "\n"
                )

                for result in results:

                    if result.get(
                        "status"
                    ) != "FAILED":

                        continue

                    file.write(
                        f"Hostname : "
                        f"{result.get('hostname', '')}\n"
                    )

                    file.write(
                        f"IP       : "
                        f"{result.get('ip', '')}\n"
                    )

                    file.write(
                        f"Reason   : "
                        f"{result.get('error', '')}\n"
                    )

                    file.write(
                        f"Output   : "
                        f"{result.get('output_file', '')}\n"
                    )

                    file.write("\n")

            # ----------------------------------------------------------
            # End
            # ----------------------------------------------------------

            file.write(
                "=" * 100 + "\n"
            )

            file.write(
                "                         END OF REPORT\n"
            )

            file.write(
                "=" * 100 + "\n"
            )

        return report_file