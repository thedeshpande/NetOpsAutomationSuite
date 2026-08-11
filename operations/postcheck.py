"""
postcheck.py
------------
Runs the Postcheck operation.
"""

from core.executor import Executor
from core.reports import ReportManager
from core.retry_manager import RetryManager


class PostcheckOperation:
    """Handles the Postcheck workflow."""

    @staticmethod
    def run(
        devices,
        site: str,
        category: str,
    ) -> list[dict] | None:
        """
        Execute Postcheck on all selected devices.

        Failed devices can be retried using the common
        RetryManager.

        Returns
        -------
        list[dict] | None
            Final execution results.
            None if the operation is aborted.
        """

        # ============================================================
        # START POSTCHECK
        # ============================================================

        print("\n")
        print("=" * 80)
        print("STARTING POSTCHECK")
        print("=" * 80)

        # ============================================================
        # INITIAL EXECUTION
        # ============================================================

        print("\nExecuting Postcheck on selected devices...\n")

        results = Executor.execute_devices(
            devices=devices,
            operation="postcheck",
        )

        # ============================================================
        # RETRY FAILED DEVICES
        # ============================================================

        results, aborted = RetryManager.run(
            devices=devices,
            results=results,
            operation="postcheck",
        )

        # ============================================================
        # ABORT CHECK
        # ============================================================

        if aborted:

            print("\n")
            print("=" * 80)
            print("POSTCHECK ABORTED")
            print("=" * 80)

            return None

        # ============================================================
        # FINAL SUMMARY
        # ============================================================

        print("\n")
        print("=" * 80)
        print("FINAL POSTCHECK SUMMARY")
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
            operation="postcheck",
            site=site,
            category=category,
            results=results,
        )

        # ============================================================
        # COMPLETED
        # ============================================================

        print("\n")
        print("=" * 80)
        print("POSTCHECK COMPLETED")
        print("=" * 80)

        print(
            f"Report : {report_file}"
        )

        print("=" * 80)

        return results