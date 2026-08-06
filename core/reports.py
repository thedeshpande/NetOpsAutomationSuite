"""
reports.py
----------
Generates execution reports for NetOps Automation Suite.
"""

from datetime import datetime
from pathlib import Path


class ReportManager:
    """Creates execution summary reports."""

    @staticmethod
    def get_reports_root() -> Path:
        """
        Returns

        reports/
        """

        project_root = Path(__file__).resolve().parent.parent

        reports_root = project_root / "reports"

        reports_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return reports_root

    @staticmethod
    def get_report_folder() -> Path:
        """
        Returns

        reports/YYYY-MM-DD/
        """

        report_folder = (
            ReportManager.get_reports_root()
            / datetime.now().strftime("%Y-%m-%d")
        )

        report_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return report_folder

    @staticmethod
    def create_report_file(
        operation: str,
    ) -> Path:
        """
        Create a timestamped report file.

        Example

        PRECHECK_Report_20260807_211500.txt
        """

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        report_name = (
            f"{operation.upper()}_Report_{timestamp}.txt"
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

        Parameters
        ----------
        operation : str

        site : str

        category : str

        results : list[dict]

        Returns
        -------
        Path
        """

        report_file = ReportManager.create_report_file(
            operation
        )

        total = len(results)

        success = sum(
            1
            for result in results
            if result["status"] == "SUCCESS"
        )

        failed = sum(
            1
            for result in results
            if result["status"] == "FAILED"
        )

        skipped = sum(
            1
            for result in results
            if result["status"] == "SKIPPED"
        )

        total_commands = sum(
            len(result.get("commands", {}))
            for result in results
        )

        with open(
            report_file,
            "w",
            encoding="utf-8",
        ) as file:

            file.write("=" * 100 + "\n")
            file.write("NetOps Automation Suite\n")
            file.write("=" * 100 + "\n\n")

            file.write(
                f"Operation : {operation.upper()}\n"
            )

            file.write(
                f"Site      : {site}\n"
            )

            file.write(
                f"Category  : {category}\n"
            )

            file.write(
                "Generated : "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            )

            file.write("\n")
            file.write("-" * 100)
            file.write("\n")

            file.write(
                f"{'Hostname':20}"
                f"{'Status':12}"
                f"{'IP Address':18}"
                "Output File\n"
            )

            file.write("-" * 100 + "\n")
                        # Write one row per device
            for result in results:

                hostname = result.get("hostname", "")
                status = result.get("status", "")
                ip = result.get("ip", "")
                output_file = result.get("output_file", "")

                file.write(
                    f"{hostname:20}"
                    f"{status:12}"
                    f"{ip:18}"
                    f"{output_file}\n"
                )

            file.write("\n")
            file.write("=" * 100)
            file.write("\n\n")

            # Summary
            file.write("SUMMARY\n")
            file.write("-" * 100 + "\n")

            executed = success + failed

            file.write(f"Total Devices      : {total}\n")
            file.write(f"Executed Devices   : {executed}\n")
            file.write(f"Successful         : {success}\n")
            file.write(f"Failed             : {failed}\n")
            file.write(f"Skipped            : {skipped}\n")
            file.write(f"Total Commands     : {total_commands}\n")

            # Failed device details
            if failed > 0:

                file.write("\n")
                file.write("FAILED DEVICES\n")
                file.write("-" * 100 + "\n")

                for result in results:

                    if result["status"] != "SUCCESS":

                        file.write(
                            f"Hostname : {result['hostname']}\n"
                        )

                        file.write(
                            f"IP       : {result['ip']}\n"
                        )

                        file.write(
                            f"Reason   : {result['error']}\n"
                        )

                        file.write("\n")

            file.write("=" * 100 + "\n")

        return report_file