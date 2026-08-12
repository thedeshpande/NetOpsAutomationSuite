"""
retry_manager.py
----------------
Common retry mechanism for NetOps Automation Suite.

Supported operations:
    - Precheck
    - Backup
    - Postcheck

Workflow:
    1. Run the operation on all selected devices.
    2. Identify failed devices.
    3. Preserve the original Execution ID.
    4. Ask the user what to do.
    5. Retry ONLY failed devices when requested.
    6. Reuse the same Execution ID for retries.
    7. Merge retry results with the original results.
    8. Repeat if devices still fail.
"""

import questionary

from core.executor import Executor


class RetryManager:
    """Common retry manager for network operations."""

    @staticmethod
    def run(
        devices,
        results,
        operation: str,
    ):
        """
        Handle failed-device retry workflow.

        Parameters
        ----------
        devices:
            Original list of selected Device objects.

        results:
            Results from the initial execution.

        operation:
            Operation name:
                precheck
                backup
                postcheck

        Returns
        -------
        tuple
            (final_results, aborted)
        """

        # ============================================================
        # FIND FAILED DEVICES
        # ============================================================

        failed_results = RetryManager.get_failed_results(
            results
        )

        # ============================================================
        # PRESERVE ORIGINAL EXECUTION ID
        # ============================================================

        execution_id = ""

        if results:
            execution_id = results[0].get(
                "execution_id",
                "",
            )

        # ------------------------------------------------------------
        # Nothing failed
        # ------------------------------------------------------------

        if not failed_results:

            return results, False

        # ============================================================
        # RETRY LOOP
        # ============================================================

        while failed_results:

            print("\n")
            print("=" * 80)
            print(f"{operation.upper()} FAILURES DETECTED")
            print("=" * 80)

            if execution_id:

                print(
                    f"Execution ID : {execution_id}"
                )

            print(
                f"\nFailed Devices : "
                f"{len(failed_results)}"
            )

            RetryManager.display_failed_devices(
                failed_results
            )

            # ========================================================
            # USER ACTION
            # ========================================================

            action = questionary.select(
                "What would you like to do?",
                choices=[
                    "Retry Failed Devices",
                    "View Failed Devices",
                    "Continue Without Retry",
                    "Abort Operation",
                ],
            ).ask()

            # ========================================================
            # QUESTIONARY CANCELLED
            # ========================================================

            if action is None:

                print("\nOperation cancelled.")

                return results, True

            # ========================================================
            # VIEW FAILED DEVICES
            # ========================================================

            if action == "View Failed Devices":

                RetryManager.display_failed_details(
                    failed_results
                )

                continue

            # ========================================================
            # CONTINUE WITHOUT RETRY
            # ========================================================

            if action == "Continue Without Retry":

                print("\n")
                print(
                    "Continuing with current results."
                )

                return results, False

            # ========================================================
            # ABORT OPERATION
            # ========================================================

            if action == "Abort Operation":

                print("\n")
                print("=" * 80)
                print(
                    f"{operation.upper()} OPERATION ABORTED"
                )

                if execution_id:

                    print(
                        f"Execution ID : {execution_id}"
                    )

                print("=" * 80)

                return results, True

            # ========================================================
            # RETRY FAILED DEVICES
            # ========================================================

            if action == "Retry Failed Devices":

                # ----------------------------------------------------
                # Convert failed results back to Device objects.
                # ----------------------------------------------------

                failed_devices = (
                    RetryManager.map_failed_devices(
                        devices=devices,
                        failed_results=failed_results,
                    )
                )

                # ----------------------------------------------------
                # Safety check
                # ----------------------------------------------------

                if not failed_devices:

                    print("\n")
                    print(
                        "ERROR: Unable to map failed "
                        "devices back to inventory."
                    )

                    print(
                        "Retry cannot be performed."
                    )

                    continue

                # ====================================================
                # RETRY ONLY FAILED DEVICES
                # ====================================================

                print("\n")
                print("=" * 80)
                print(
                    f"RETRYING FAILED "
                    f"{operation.upper()} DEVICES"
                )
                print("=" * 80)

                if execution_id:

                    print(
                        f"\nExecution ID : "
                        f"{execution_id}"
                    )

                print(
                    f"\nRetrying "
                    f"{len(failed_devices)} "
                    f"failed device(s) only.\n"
                )

                # ----------------------------------------------------
                # IMPORTANT:
                # Reuse the SAME Execution ID.
                # ----------------------------------------------------

                retry_results = Executor.execute_devices(
                    devices=failed_devices,
                    operation=operation,
                    execution_id=execution_id,
                )

                # ====================================================
                # RETRY SUMMARY
                # ====================================================

                recovered = [
                    result
                    for result in retry_results
                    if result.get("status") == "SUCCESS"
                ]

                still_failed = [
                    result
                    for result in retry_results
                    if result.get("status") == "FAILED"
                ]

                print("\n")
                print("=" * 80)
                print("RETRY SUMMARY")
                print("=" * 80)

                if execution_id:

                    print(
                        f"Execution ID      : "
                        f"{execution_id}"
                    )

                print(
                    f"Previously Failed : "
                    f"{len(failed_results)}"
                )

                print(
                    f"Retried           : "
                    f"{len(retry_results)}"
                )

                print(
                    f"Recovered         : "
                    f"{len(recovered)}"
                )

                print(
                    f"Still Failed      : "
                    f"{len(still_failed)}"
                )

                # ====================================================
                # RECOVERED DEVICES
                # ====================================================

                if recovered:

                    print("\nRecovered Devices")
                    print("-" * 80)

                    for result in recovered:

                        print(
                            f"{result.get('hostname', ''):<25}"
                            f"{result.get('ip', ''):<20}"
                            "SUCCESS"
                        )

                # ====================================================
                # STILL FAILED DEVICES
                # ====================================================

                if still_failed:

                    print("\nStill Failed")
                    print("-" * 80)

                    for result in still_failed:

                        print(
                            f"{result.get('hostname', ''):<25}"
                            f"{result.get('ip', ''):<20}"
                            "FAILED"
                        )

                print("-" * 80)

                # ====================================================
                # MERGE RETRY RESULTS
                # ====================================================

                results = RetryManager.merge_results(
                    original_results=results,
                    retry_results=retry_results,
                )

                # ====================================================
                # FIND FAILURES AGAIN
                # ====================================================

                failed_results = (
                    RetryManager.get_failed_results(
                        results
                    )
                )

                # ====================================================
                # ALL DEVICES NOW PASS
                # ====================================================

                if not failed_results:

                    print("\n")
                    print("=" * 80)
                    print(
                        f"ALL {operation.upper()} "
                        "DEVICES PASSED"
                    )

                    if execution_id:

                        print(
                            f"Execution ID : "
                            f"{execution_id}"
                        )

                    print("=" * 80)

                    return results, False

                # ====================================================
                # DEVICES STILL FAIL
                # ====================================================

                print("\n")

                print(
                    f"{len(failed_results)} device(s) "
                    "are still failing."
                )

                # Loop returns to failure menu.

        return results, False

    # ==================================================================
    # GET FAILED RESULTS
    # ==================================================================

    @staticmethod
    def get_failed_results(results):
        """
        Return only failed execution results.
        """

        return [
            result
            for result in results
            if result.get("status") == "FAILED"
        ]

    # ==================================================================
    # MAP FAILED RESULTS TO DEVICES
    # ==================================================================

    @staticmethod
    def map_failed_devices(
        devices,
        failed_results,
    ):
        """
        Convert failed results back into Device objects.

        Management IP is used as the lookup key.
        """

        device_map = {}

        for device in devices:

            management_ip = getattr(
                device,
                "management_ip",
                None,
            )

            if management_ip:

                device_map[
                    management_ip
                ] = device

        failed_devices = []

        for result in failed_results:

            failed_ip = result.get("ip")

            device = device_map.get(
                failed_ip
            )

            if device is not None:

                failed_devices.append(
                    device
                )

        return failed_devices

    # ==================================================================
    # MERGE RESULTS
    # ==================================================================

    @staticmethod
    def merge_results(
        original_results,
        retry_results,
    ):
        """
        Replace old failed results with retry results.

        Example:

            Initial:

            R1 -> SUCCESS
            R2 -> FAILED
            R3 -> SUCCESS
            R4 -> FAILED

            Retry:

            R2 -> SUCCESS
            R4 -> FAILED

            Final:

            R1 -> SUCCESS
            R2 -> SUCCESS
            R3 -> SUCCESS
            R4 -> FAILED
        """

        retry_map = {
            result.get("ip"): result
            for result in retry_results
        }

        final_results = []

        for result in original_results:

            ip = result.get("ip")

            if ip in retry_map:

                final_results.append(
                    retry_map[ip]
                )

            else:

                final_results.append(
                    result
                )

        return final_results

    # ==================================================================
    # DISPLAY FAILED DEVICES
    # ==================================================================

    @staticmethod
    def display_failed_devices(
        failed_results,
    ):
        """
        Display a compact list of failed devices.
        """

        print("\nFailed Devices")
        print("-" * 80)

        print(
            f"{'Hostname':<25}"
            f"{'IP Address':<20}"
            "Error"
        )

        print("-" * 80)

        for result in failed_results:

            hostname = str(
                result.get(
                    "hostname",
                    "",
                )
            )

            ip = str(
                result.get(
                    "ip",
                    "",
                )
            )

            error = str(
                result.get(
                    "error",
                    "",
                )
            ).replace(
                "\n",
                " ",
            )

            if len(error) > 45:

                error = (
                    error[:42]
                    + "..."
                )

            print(
                f"{hostname:<25}"
                f"{ip:<20}"
                f"{error}"
            )

        print("-" * 80)

    # ==================================================================
    # DISPLAY FAILED DETAILS
    # ==================================================================

    @staticmethod
    def display_failed_details(
        failed_results,
    ):
        """
        Display detailed information about failed devices.
        """

        print("\n")
        print("=" * 80)
        print("FAILED DEVICE DETAILS")
        print("=" * 80)

        for result in failed_results:

            print()

            if result.get("execution_id"):

                print(
                    f"Execution ID : "
                    f"{result.get('execution_id', '')}"
                )

            print(
                f"Hostname : "
                f"{result.get('hostname', '')}"
            )

            print(
                f"IP       : "
                f"{result.get('ip', '')}"
            )

            print(
                f"Category : "
                f"{result.get('category', '')}"
            )

            print(
                f"Profile  : "
                f"{result.get('profile', '')}"
            )

            print(
                f"Reason   : "
                f"{result.get('error', '')}"
            )

            output_file = result.get(
                "output_file",
                "",
            )

            if output_file:

                print(
                    f"Output   : "
                    f"{output_file}"
                )

            print("-" * 80)