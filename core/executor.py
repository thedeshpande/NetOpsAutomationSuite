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

    @staticmethod
    def execute_device(
        device: Device,
        operation: str,
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

        Returns
        -------
        dict
        """

        result = {
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
            "execution_start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "execution_end": "",
        }

        connection = None

        try:

            LoggerManager.info(
                f"Connecting to {device.hostname} ({device.management_ip})"
            )

            # Validate profile exists before attempting SSH
            ProfileManager.load_profile(device.profile)

            # Load commands for this profile
            commands = ProfileManager.load_commands(
                device.profile,
                operation,
            )

            if not commands:
                result["error"] = "No commands found."
                result["execution_end"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                LoggerManager.error(
                    f"No commands found for {device.hostname} ({device.management_ip})"
                )

                return result

            # Retry SSH connection up to 3 times for connection-related errors
            max_attempts = 3
            for attempt in range(1, max_attempts + 1):
                try:
                    LoggerManager.info(
                        f"Connection attempt {attempt}/{max_attempts} for {device.hostname} ({device.management_ip})"
                    )

                    connection = ConnectionManager.connect(
                        device
                    )

                    LoggerManager.info(
                        f"Connected successfully to {device.hostname} ({device.management_ip})"
                    )
                    break

                except (ConnectionError, TimeoutError) as error:
                    LoggerManager.error(
                        f"Connection attempt {attempt}/{max_attempts} failed for {device.hostname} ({device.management_ip}): {error}"
                    )

                    if attempt == max_attempts:
                        raise

                    LoggerManager.info(
                        f"Retrying connection to {device.hostname} ({device.management_ip}) in 5 seconds"
                    )
                    time.sleep(5)

            LoggerManager.info(
                f"Executing commands on {device.hostname} ({device.management_ip})"
            )

            # Execute commands
            outputs = ConnectionManager.execute_commands(
                connection,
                commands,
            )

            LoggerManager.info(
                f"Saving output for {device.hostname} ({device.management_ip})"
            )

            # Save command outputs
            output_file = OutputManager.save_output(
                device=device,
                operation=operation,
                command_outputs=outputs,
            )

            result["commands"] = outputs
            result["output_file"] = str(output_file)
            result["status"] = "SUCCESS"
            result["execution_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            LoggerManager.success(
                f"Completed successfully for {device.hostname} ({device.management_ip})"
            )

        except Exception as error:

            result["error"] = str(error)
            result["execution_end"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            LoggerManager.error(
                f"Failed for {device.hostname} ({device.management_ip}) with exception: {error}"
            )

            failed_file = OutputManager.save_failed_output(
                device=device,
                operation=operation,
                error=str(error),
            )

            result["output_file"] = str(failed_file)

        finally:

            LoggerManager.info(
                f"Disconnecting from {device.hostname} ({device.management_ip})"
            )

            ConnectionManager.disconnect(connection)

        return result

    @staticmethod
    def execute_devices(
        devices: list[Device],
        operation: str,
        max_workers: int = 10,
    ) -> list[dict]:
        """
        Execute an operation on multiple devices.

        Parameters
        ----------
        devices : list[Device]

        operation : str

        max_workers : int
            Number of worker threads.

        Returns
        -------
        list[dict]
            Execution results for every device.
        """

        results = []

        total_devices = len(devices)

        LoggerManager.info(
            f"Starting {operation.upper()} execution for {total_devices} devices"
        )

        print("\n")
        print("=" * 80)
        print(f"Starting {operation.upper()}")
        print(f"Devices Found : {total_devices}")
        print("=" * 80)
        print()

        seen_ips = set()
        devices_to_execute = []

        for device in devices:
            if device.management_ip in seen_ips:
                skipped_result = {
                    "hostname": device.hostname,
                    "ip": device.management_ip,
                    "site": device.site,
                    "category": device.category,
                    "profile": device.profile,
                    "operation": operation,
                    "status": "SKIPPED",
                    "output_file": "",
                    "commands": {},
                    "error": "Duplicate management IP.",
                    "execution_start": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "execution_end": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }

                LoggerManager.info(
                    f"Skipped duplicate device {device.hostname} ({device.management_ip})"
                )

                results.append(skipped_result)
            else:
                seen_ips.add(device.management_ip)
                devices_to_execute.append(device)

        total_to_execute = len(devices_to_execute)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_device = {}
            future_start_times = {}

            for device in devices_to_execute:
                future = executor.submit(
                    Executor.execute_device,
                    device,
                    operation,
                )
                future_to_device[future] = device
                future_start_times[future] = time.perf_counter()

            completed_count = 0

            print(
                f"{'Progress':<10}"
                f"{'Hostname':<24}"
                f"{'IP Address':<18}"
                f"{'Status':<12}"
                f"Execution Time"
            )
            print("-" * 80)

            for future in as_completed(future_to_device):
                completed_count += 1
                device = future_to_device[future]
                start_time = future_start_times.get(future, time.perf_counter())
                duration = time.perf_counter() - start_time

                try:
                    result = future.result()
                except Exception as error:
                    result = {
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
                    }

                status = result["status"]
                status_display = result["status"]

                LoggerManager.info(
                    f"Completed [{completed_count}/{total_to_execute}] for {device.hostname} ({device.management_ip})"
                )

                print(
                    f"[{completed_count}/{total_to_execute}] "
                    f"{device.hostname:<24}"
                    f"{device.management_ip:<18}"
                    f"{status_display:<12}"
                    f"{duration:.1f}s"
                )

                if status == "SUCCESS":
                    print("   ✅ SUCCESS")
                elif status == "FAILED":
                    print(f"   ❌ FAILED : {result['error']}")
                else:
                    print("   ⚠️ SKIPPED")

                results.append(result)

        return results

    @staticmethod
    def get_summary(
        results: list[dict],
    ) -> dict:
        """
        Build execution summary.

        Parameters
        ----------
        results : list[dict]

        Returns
        -------
        dict
        """

        summary = {
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
            status = result.get("status")

            if status == "SUCCESS":
                summary["success"] += 1
                summary["executed_devices"] += 1
                summary["successful_devices"].append(
                    result["hostname"]
                )

            elif status == "FAILED":
                summary["failed"] += 1
                summary["executed_devices"] += 1
                summary["failed_devices"].append(
                    result["hostname"]
                )

            elif status == "SKIPPED":
                summary["skipped"] += 1
                summary["skipped_devices"].append(
                    result["hostname"]
                )

            commands = result.get("commands") or {}
            summary["total_commands"] += len(commands)

            start = result.get("execution_start")
            end = result.get("execution_end")
            if start and end:
                try:
                    start_dt = datetime.strptime(
                        start,
                        "%Y-%m-%d %H:%M:%S"
                    )
                    end_dt = datetime.strptime(
                        end,
                        "%Y-%m-%d %H:%M:%S"
                    )
                    total_seconds += (
                        end_dt - start_dt
                    ).total_seconds()
                except Exception:
                    pass

        summary["execution_time_total"] = (
            f"{total_seconds:.1f}s"
        )

        return summary

    @staticmethod
    def print_summary(
        summary: dict,
    ) -> None:
        """
        Display execution summary.
        """

        print("\n")
        print("=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)

        print(f"Total Devices : {summary['total']}")
        print(f"Successful    : {summary['success']}")
        print(f"Failed        : {summary['failed']}")

        if summary["failed_devices"]:

            print("\nFailed Devices")

            print("-" * 80)

            for hostname in summary["failed_devices"]:
                print(hostname)

        print("=" * 80)