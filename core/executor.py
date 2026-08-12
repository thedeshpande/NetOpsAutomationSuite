"""
executor.py
-----------
Execution engine for NetOps Automation Suite.

Responsibilities
----------------
- Connect to devices
- Load operation commands
- Execute commands
- Save outputs
- Disconnect
- Return execution results
- Generate and track Execution ID
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from models.device import Device

from core.connection import ConnectionManager
from core.profiles import ProfileManager
from core.output import OutputManager
from core.logger import LoggerManager


class Executor:
    """Execution engine."""

    # =========================================================================
    # EXECUTION ID
    # =========================================================================

    @staticmethod
    def generate_execution_id() -> str:
        """
        Generate a unique Execution ID for one automation run.

        Example
        -------
        EXEC-20260813-214530
        """

        return (
            f"EXEC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

    # =========================================================================
    # EXECUTE ONE DEVICE
    # =========================================================================

    @staticmethod
    def execute_device(
        device: Device,
        operation: str,
        execution_id: str = "",
    ) -> dict:
        """
        Execute one operation on one device.

        Parameters
        ----------
        device : Device

        operation : str
            precheck
            postcheck
            backup

        execution_id : str
            Unique ID for the current automation run.

        Returns
        -------
        dict
            Execution result.
        """

        # ---------------------------------------------------------------------
        # Generate an ID if this method is called directly without one.
        # ---------------------------------------------------------------------

        if not execution_id:

            execution_id = (
                Executor.generate_execution_id()
            )

        # ---------------------------------------------------------------------
        # Initial Result Object
        # ---------------------------------------------------------------------

        result = {
            "execution_id": execution_id,
            "hostname": device.hostname,
            "ip": device.management_ip,
            "site": device.site,
            "category": device.category,
            "profile": device.profile,
            "operation": operation,
            "status": "FAILED",
            "output_file": "",
            "commands": {},
            "error": "",
            "execution_start": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "execution_end": "",
        }

        connection = None

        # =========================================================================
        # DEVICE EXECUTION
        # =========================================================================

        try:

            LoggerManager.info(
                f"[{execution_id}] Connecting to "
                f"{device.hostname} "
                f"({device.management_ip})"
            )

            # ---------------------------------------------------------------------
            # Validate profile
            # ---------------------------------------------------------------------

            ProfileManager.load_profile(
                device.profile
            )

            # ---------------------------------------------------------------------
            # Load commands
            # ---------------------------------------------------------------------

            commands = ProfileManager.load_commands(
                device.profile,
                operation,
            )

            if not commands:

                result["error"] = (
                    "No commands found."
                )

                result["execution_end"] = (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )

                LoggerManager.error(
                    f"[{execution_id}] No commands found for "
                    f"{device.hostname} "
                    f"({device.management_ip})"
                )

                return result

            # =========================================================================
            # SSH CONNECTION RETRIES
            # =========================================================================

            max_attempts = 3

            for attempt in range(
                1,
                max_attempts + 1,
            ):

                try:

                    LoggerManager.info(
                        f"[{execution_id}] "
                        f"Connection attempt "
                        f"{attempt}/{max_attempts} "
                        f"for {device.hostname} "
                        f"({device.management_ip})"
                    )

                    connection = (
                        ConnectionManager.connect(
                            device
                        )
                    )

                    LoggerManager.info(
                        f"[{execution_id}] "
                        f"Connected successfully to "
                        f"{device.hostname} "
                        f"({device.management_ip})"
                    )

                    break

                except (
                    ConnectionError,
                    TimeoutError,
                ) as error:

                    LoggerManager.error(
                        f"[{execution_id}] "
                        f"Connection attempt "
                        f"{attempt}/{max_attempts} "
                        f"failed for "
                        f"{device.hostname} "
                        f"({device.management_ip}): "
                        f"{error}"
                    )

                    if attempt == max_attempts:

                        raise

                    LoggerManager.info(
                        f"[{execution_id}] "
                        f"Retrying connection to "
                        f"{device.hostname} "
                        f"({device.management_ip}) "
                        f"in 5 seconds"
                    )

                    time.sleep(5)

            # =========================================================================
            # EXECUTE COMMANDS
            # =========================================================================

            LoggerManager.info(
                f"[{execution_id}] "
                f"Executing commands on "
                f"{device.hostname} "
                f"({device.management_ip})"
            )

            outputs = (
                ConnectionManager.execute_commands(
                    connection,
                    commands,
                )
            )

            # =========================================================================
            # SAVE OUTPUT
            # =========================================================================

            LoggerManager.info(
                f"[{execution_id}] "
                f"Saving output for "
                f"{device.hostname} "
                f"({device.management_ip})"
            )

            output_file = (
                OutputManager.save_output(
                    device=device,
                    operation=operation,
                    command_outputs=outputs,
                    execution_id=execution_id,
                )
            )

            # =========================================================================
            # SUCCESS
            # =========================================================================

            result["commands"] = outputs

            result["output_file"] = (
                str(output_file)
            )

            result["status"] = "SUCCESS"

            result["execution_end"] = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            LoggerManager.success(
                f"[{execution_id}] "
                f"Completed successfully for "
                f"{device.hostname} "
                f"({device.management_ip})"
            )

        # =========================================================================
        # DEVICE FAILURE
        # =========================================================================

        except Exception as error:

            result["error"] = str(error)

            result["execution_end"] = (
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            LoggerManager.error(
                f"[{execution_id}] "
                f"Failed for "
                f"{device.hostname} "
                f"({device.management_ip}) "
                f"with exception: {error}"
            )

            # ---------------------------------------------------------------------
            # Save failure details
            # ---------------------------------------------------------------------

            try:

                failed_file = (
                    OutputManager.save_failed_output(
                        device=device,
                        operation=operation,
                        error=str(error),
                        execution_id=execution_id,
                    )
                )

                result["output_file"] = (
                    str(failed_file)
                )

            except Exception as output_error:

                LoggerManager.error(
                    f"[{execution_id}] "
                    f"Unable to save failure output "
                    f"for {device.hostname}: "
                    f"{output_error}"
                )

        # =========================================================================
        # ALWAYS DISCONNECT
        # =========================================================================

        finally:

            LoggerManager.info(
                f"[{execution_id}] "
                f"Disconnecting from "
                f"{device.hostname} "
                f"({device.management_ip})"
            )

            ConnectionManager.disconnect(
                connection
            )

        return result

    # =========================================================================
    # EXECUTE MULTIPLE DEVICES
    # =========================================================================

    @staticmethod
    def execute_devices(
        devices: list[Device],
        operation: str,
        max_workers: int = 10,
        execution_id: str = "",
    ) -> list[dict]:
        """
        Execute an operation on multiple devices.

        Parameters
        ----------
        devices : list[Device]

        operation : str

        max_workers : int
            Number of worker threads.

        execution_id : str
            Optional existing Execution ID.

            If not supplied, a new Execution ID is generated.

            Retry operations can reuse the original Execution ID.

        Returns
        -------
        list[dict]
            Execution results for every device.
        """

        # =========================================================================
        # EXECUTION ID
        # =========================================================================

        if not execution_id:

            execution_id = (
                Executor.generate_execution_id()
            )

        results = []

        total_devices = len(
            devices
        )

        LoggerManager.info(
            f"[{execution_id}] Starting "
            f"{operation.upper()} execution "
            f"for {total_devices} devices"
        )

        # =========================================================================
        # EXECUTION HEADER
        # =========================================================================

        print("\n")

        print(
            "=" * 80
        )

        print(
            "NETOPS AUTOMATION SUITE"
        )

        print(
            "=" * 80
        )

        print(
            f"Execution ID  : {execution_id}"
        )

        print(
            f"Operation     : {operation.upper()}"
        )

        print(
            f"Devices Found : {total_devices}"
        )

        print(
            "=" * 80
        )

        print()

        # =========================================================================
        # DUPLICATE IP CHECK
        # =========================================================================

        seen_ips = set()

        devices_to_execute = []

        for device in devices:

            if device.management_ip in seen_ips:

                skipped_result = {
                    "execution_id": execution_id,
                    "hostname": device.hostname,
                    "ip": device.management_ip,
                    "site": device.site,
                    "category": device.category,
                    "profile": device.profile,
                    "operation": operation,
                    "status": "SKIPPED",
                    "output_file": "",
                    "commands": {},
                    "error": (
                        "Duplicate management IP."
                    ),
                    "execution_start": (
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    ),
                    "execution_end": (
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    ),
                }

                LoggerManager.info(
                    f"[{execution_id}] "
                    f"Skipped duplicate device "
                    f"{device.hostname} "
                    f"({device.management_ip})"
                )

                results.append(
                    skipped_result
                )

            else:

                seen_ips.add(
                    device.management_ip
                )

                devices_to_execute.append(
                    device
                )

        total_to_execute = len(
            devices_to_execute
        )

        # =========================================================================
        # PARALLEL EXECUTION
        # =========================================================================

        if total_to_execute == 0:

            return results

        with ThreadPoolExecutor(
            max_workers=max_workers
        ) as executor:

            future_to_device = {}

            future_start_times = {}

            # ---------------------------------------------------------------------
            # Submit jobs
            # ---------------------------------------------------------------------

            for device in devices_to_execute:

                future = executor.submit(
                    Executor.execute_device,
                    device,
                    operation,
                    execution_id,
                )

                future_to_device[
                    future
                ] = device

                future_start_times[
                    future
                ] = time.perf_counter()

            # ---------------------------------------------------------------------
            # Progress Header
            # ---------------------------------------------------------------------

            completed_count = 0

            print(
                f"{'Progress':<10}"
                f"{'Hostname':<24}"
                f"{'IP Address':<18}"
                f"{'Status':<12}"
                f"Execution Time"
            )

            print(
                "-" * 80
            )

            # ---------------------------------------------------------------------
            # Process completed futures
            # ---------------------------------------------------------------------

            for future in as_completed(
                future_to_device
            ):

                completed_count += 1

                device = future_to_device[
                    future
                ]

                start_time = (
                    future_start_times.get(
                        future,
                        time.perf_counter(),
                    )
                )

                duration = (
                    time.perf_counter()
                    - start_time
                )

                try:

                    result = future.result()

                except Exception as error:

                    result = {
                        "execution_id": execution_id,
                        "hostname": device.hostname,
                        "ip": device.management_ip,
                        "site": device.site,
                        "category": device.category,
                        "profile": device.profile,
                        "operation": operation,
                        "status": "FAILED",
                        "output_file": "",
                        "commands": {},
                        "error": str(error),
                        "execution_start": "",
                        "execution_end": "",
                    }

                status = result[
                    "status"
                ]

                # -----------------------------------------------------------------
                # Logging
                # -----------------------------------------------------------------

                LoggerManager.info(
                    f"[{execution_id}] "
                    f"Completed "
                    f"[{completed_count}/"
                    f"{total_to_execute}] "
                    f"for {device.hostname} "
                    f"({device.management_ip})"
                )

                # -----------------------------------------------------------------
                # Progress Display
                # -----------------------------------------------------------------

                print(
                    f"[{completed_count}/"
                    f"{total_to_execute}] "
                    f"{device.hostname:<24}"
                    f"{device.management_ip:<18}"
                    f"{status:<12}"
                    f"{duration:.1f}s"
                )

                if status == "SUCCESS":

                    print(
                        "   ✅ SUCCESS"
                    )

                elif status == "FAILED":

                    print(
                        f"   ❌ FAILED : "
                        f"{result['error']}"
                    )

                else:

                    print(
                        "   ⚠️ SKIPPED"
                    )

                results.append(
                    result
                )

        return results

    # =========================================================================
    # SUMMARY
    # =========================================================================

    @staticmethod
    def get_summary(
        results: list[dict],
    ) -> dict:
        """
        Build execution summary.
        """

        execution_id = ""

        if results:

            execution_id = (
                results[0].get(
                    "execution_id",
                    "",
                )
            )

        summary = {
            "execution_id": execution_id,
            "total": len(results),
            "success": 0,
            "failed": 0,
            "skipped": 0,
            "executed_devices": 0,
            "total_commands": 0,
            "execution_time_total": "0.0s",
            "successful_devices": [],
            "failed_devices": [],
            "skipped_devices": [],
        }

        total_seconds = 0.0

        for result in results:

            status = result.get(
                "status"
            )

            # ---------------------------------------------------------------------
            # SUCCESS
            # ---------------------------------------------------------------------

            if status == "SUCCESS":

                summary["success"] += 1

                summary[
                    "executed_devices"
                ] += 1

                summary[
                    "successful_devices"
                ].append(
                    result["hostname"]
                )

            # ---------------------------------------------------------------------
            # FAILED
            # ---------------------------------------------------------------------

            elif status == "FAILED":

                summary["failed"] += 1

                summary[
                    "executed_devices"
                ] += 1

                summary[
                    "failed_devices"
                ].append(
                    result["hostname"]
                )

            # ---------------------------------------------------------------------
            # SKIPPED
            # ---------------------------------------------------------------------

            elif status == "SKIPPED":

                summary["skipped"] += 1

                summary[
                    "skipped_devices"
                ].append(
                    result["hostname"]
                )

            # ---------------------------------------------------------------------
            # COMMAND COUNT
            # ---------------------------------------------------------------------

            commands = (
                result.get(
                    "commands"
                )
                or {}
            )

            summary[
                "total_commands"
            ] += len(commands)

            # ---------------------------------------------------------------------
            # EXECUTION TIME
            # ---------------------------------------------------------------------

            start = result.get(
                "execution_start"
            )

            end = result.get(
                "execution_end"
            )

            if start and end:

                try:

                    start_dt = (
                        datetime.strptime(
                            start,
                            "%Y-%m-%d %H:%M:%S",
                        )
                    )

                    end_dt = (
                        datetime.strptime(
                            end,
                            "%Y-%m-%d %H:%M:%S",
                        )
                    )

                    total_seconds += (
                        end_dt - start_dt
                    ).total_seconds()

                except Exception:

                    pass

        summary[
            "execution_time_total"
        ] = (
            f"{total_seconds:.1f}s"
        )

        return summary

    # =========================================================================
    # PRINT SUMMARY
    # =========================================================================

    @staticmethod
    def print_summary(
        summary: dict,
    ) -> None:
        """
        Display execution summary.
        """

        print("\n")

        print(
            "=" * 80
        )

        print(
            "EXECUTION SUMMARY"
        )

        print(
            "=" * 80
        )

        print(
            f"Execution ID : "
            f"{summary.get('execution_id', '')}"
        )

        print(
            f"Total Devices : "
            f"{summary['total']}"
        )

        print(
            f"Successful    : "
            f"{summary['success']}"
        )

        print(
            f"Failed        : "
            f"{summary['failed']}"
        )

        print(
            f"Skipped       : "
            f"{summary['skipped']}"
        )

        print(
            f"Commands      : "
            f"{summary['total_commands']}"
        )

        print(
            f"Execution Time: "
            f"{summary['execution_time_total']}"
        )

        # ---------------------------------------------------------------------
        # Failed Devices
        # ---------------------------------------------------------------------

        if summary[
            "failed_devices"
        ]:

            print(
                "\nFailed Devices"
            )

            print(
                "-" * 80
            )

            for hostname in (
                summary[
                    "failed_devices"
                ]
            ):

                print(
                    hostname
                )

        print(
            "=" * 80
        )