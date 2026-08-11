"""
backup.py
---------
Runs the Backup operation.
"""

from core.executor import Executor
from core.reports import ReportManager
from core.retry_manager import RetryManager


class BackupOperation:
    """Handles the Backup workflow."""

    @staticmethod
    def run(
        devices,
        site: str,
        category: str,
    ) -> list[dict] | None:
        """
        Execute Backup on all selected devices.

        Failed devices can be retried using the common
        RetryManager.

        Returns
        -------
        list[dict] | None
            Final execution results.
            None if the operation is aborted.
        """

        # ============================================================
        # START BACKUP
        # ============================================================

        print("\n")
        print("=" * 80)
        print("STARTING BACKUP")
        print("=" * 80)

        # ============================================================
        # INITIAL EXECUTION
        # ============================================================

        print("\nExecuting Backup on selected devices...\n")

        results = Executor.execute_devices(
            devices=devices,
            operation="backup",
        )

        # ============================================================
        # RETRY FAILED DEVICES
        # ============================================================

        results, aborted = RetryManager.run(
            devices=devices,
            results=results,
            operation="backup",
        )

        # ============================================================
        # ABORT CHECK
        # ============================================================

        if aborted:

            print("\n")
            print("=" * 80)
            print("BACKUP ABORTED")
            print("=" * 80)

            return None

        # ============================================================
        # FINAL SUMMARY
        # ============================================================

        print("\n")
        print("=" * 80)
        print("FINAL BACKUP SUMMARY")
        print("=" * 80)

        summary = Executor.get_summary(
            results
        )

        Executor.print_summary(
            summary
        )

        # ============================================================
        # GENERATE FINAL REPORT
        # ============================================================

        report_file = ReportManager.generate(
            operation="backup",
            site=site,
            category=category,
            results=results,
        )

        # ============================================================
        # COMPLETED
        # ============================================================

        print("\n")
        print("=" * 80)
        print("BACKUP COMPLETED")
        print("=" * 80)

        print(
            f"Report : {report_file}"
        )

        print("=" * 80)

        return results