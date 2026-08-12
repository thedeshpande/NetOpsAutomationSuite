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
        execution_id: str,
    ) -> list[dict]:
        """
        Execute Postcheck on selected devices.
        """

        print("\n")
        print("=" * 80)
        print("STARTING POSTCHECK")
        print("=" * 80)

        print(
            f"Execution ID : {execution_id}"
        )

        print("=" * 80)

        # Execute commands
        results = Executor.execute_devices(
            devices=devices,
            operation="postcheck",
            execution_id=execution_id,
        )

        # Build summary
        summary = Executor.get_summary(
            results
        )

        # Print summary
        Executor.print_summary(
            summary
        )

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

        print(
            f"Execution ID : {execution_id}"
        )

        print(
            f"Report       : {report_file}"
        )

        print("=" * 80)

        return results