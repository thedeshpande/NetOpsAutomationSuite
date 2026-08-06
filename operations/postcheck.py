"""
postcheck.py
------------
Runs the Postcheck operation.
"""

from core.executor import Executor
from core.reports import ReportManager


class PostcheckOperation:
    """Handles the Postcheck workflow."""

    @staticmethod
    def run(
        devices,
        site: str,
        category: str,
    ) -> list[dict]:
        """
        Execute Postcheck on the selected devices.

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
        list[dict]
            Execution results.
        """

        print("\n")
        print("=" * 80)
        print("STARTING POSTCHECK")
        print("=" * 80)

        # Execute commands on all devices
        results = Executor.execute_devices(
            devices=devices,
            operation="postcheck",
        )

        # Build execution summary
        summary = Executor.get_summary(results)

        # Print summary to console
        Executor.print_summary(summary)

        # Generate report
        report_file = ReportManager.generate(
            operation="postcheck",
            site=site,
            category=category,
            results=results,
        )

        print("\n")
        print("=" * 80)
        print("POSTCHECK COMPLETED")
        print("=" * 80)
        print(f"Report : {report_file}")
        print("=" * 80)

        return results