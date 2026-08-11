"""
precheck.py
-----------
Runs the Precheck operation.
"""

from core.executor import Executor
from core.reports import ReportManager
from core.retry_manager import RetryManager


class PrecheckOperation:
    """Handles the Precheck workflow."""

    @staticmethod
    def run(
        devices,
        site: str,
        category: str,
    ) -> list[dict] | None:
        """
        Execute Precheck on all selected devices.

        If any devices fail, RetryManager allows the user to:

        1. Retry failed devices
        2. View failed devices
        3. Continue without retry
        4. Abort the operation

        Only failed devices are executed during a retry.

        Parameters
        ----------
        devices : list[Device]
            Filtered devices.

        site : str
            Selected site.

        category : str
            Selected device category.

        Returns
        -------
        list[dict] | None
            Final execution results.

            None is returned when the user aborts
            the operation.
        """

        # ============================================================
        # START PRECHECK
        # ============================================================

        print("\n")
        print("=" * 80)
        print("STARTING PRECHECK")
        print("=" * 80)

        # ============================================================
        # INITIAL EXECUTION
        # ============================================================

        print("\nExecuting Precheck on selected devices...\n")

        results = Executor.execute_devices(
            devices=devices,
            operation="precheck",
        )

        # ============================================================
        # RETRY FAILED DEVICES
        # ============================================================

        results, aborted = RetryManager.run(
            devices=devices,
            results=results,
            operation="precheck",
        )

        # ============================================================
        # ABORT CHECK
        # ============================================================

        if aborted:

            print("\n")
            print("=" * 80)
            print("PRECHECK ABORTED")
            print("=" * 80)

            return None

        # ============================================================
        # FINAL SUMMARY
        # ============================================================

        print("\n")
        print("=" * 80)
        print("FINAL PRECHECK SUMMARY")
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
            operation="precheck",
            site=site,
            category=category,
            results=results,
        )

        # ============================================================
        # COMPLETED
        # ============================================================

        print("\n")
        print("=" * 80)
        print("PRECHECK COMPLETED")
        print("=" * 80)

        print(
            f"Report : {report_file}"
        )

        print("=" * 80)

        return results