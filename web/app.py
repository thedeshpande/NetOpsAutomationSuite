"""
===============================================================================
File Name   : app.py
Project     : NetOps Automation Suite
Description : Flask Web Interface
===============================================================================

Responsibilities
----------------
- Serve NetOps Automation Suite UI
- Load network inventory
- Provide inventory information
- Filter devices
- Execute Precheck
- Execute Postcheck
- Execute Backup
- Retry failed devices
- Return execution results to frontend

The existing CLI automation engine remains the source of truth.
===============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    jsonify,
    render_template,
    request,
)


# =============================================================================
# PROJECT ROOT
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# =============================================================================
# EXISTING NETOPS MODULES
# =============================================================================

from core.inventory import Inventory
from core.filters import DeviceFilter
from core.executor import Executor
from operations.precheck import PrecheckOperation
from operations.postcheck import PostcheckOperation
from operations.backup import BackupOperation


# =============================================================================
# FLASK APPLICATION
# =============================================================================

app = Flask(__name__)


# =============================================================================
# DEVICE SERIALIZATION
# =============================================================================

def device_to_dict(device):
    """
    Convert Device object into JSON-safe dictionary.
    """

    return {
        "status": getattr(
            device,
            "status",
            "",
        ),

        "site": getattr(
            device,
            "site",
            "",
        ),

        "hostname": getattr(
            device,
            "hostname",
            "",
        ),

        "ip": getattr(
            device,
            "management_ip",
            "",
        ),

        "category": getattr(
            device,
            "category",
            "",
        ),

        "profile": getattr(
            device,
            "profile",
            "",
        ),

        "platform": getattr(
            device,
            "platform",
            "",
        ),

        "os": getattr(
            device,
            "os",
            "",
        ),

        "vendor": getattr(
            device,
            "vendor",
            "",
        ),

        "credential_profile": getattr(
            device,
            "credential_profile",
            "",
        ),
    }


# =============================================================================
# FORMAT EXECUTION RESULTS
# =============================================================================

def format_execution_results(
    results,
    default_site="",
    default_category="",
    default_execution_id="",
):
    """
    Convert executor results into frontend-friendly dictionaries.
    """

    device_results = []

    for result in results:

        device_results.append(
            {
                "hostname": result.get(
                    "hostname",
                    "",
                ),

                "ip": result.get(
                    "ip",
                    "",
                ),

                "site": result.get(
                    "site",
                    default_site,
                ),

                "category": result.get(
                    "category",
                    default_category,
                ),

                "status": result.get(
                    "status",
                    "FAILED",
                ),

                "error": result.get(
                    "error",
                    "",
                ),

                "output_file": result.get(
                    "output_file",
                    "",
                ),

                "execution_id": result.get(
                    "execution_id",
                    default_execution_id,
                ),
            }
        )

    return device_results


# =============================================================================
# BUILD EXECUTION RESPONSE
# =============================================================================

def build_execution_response(
    operation,
    site,
    category,
    execution_id,
    results,
):
    """
    Build a consistent JSON response for both
    initial execution and retry execution.
    """

    summary = Executor.get_summary(
        results
    )

    device_results = format_execution_results(
        results=results,
        default_site=site,
        default_category=category,
        default_execution_id=execution_id,
    )

    return {
        "success": True,

        "execution_id": execution_id,

        "operation": operation.upper(),

        "site": site,

        "category": category,

        "summary": {
            "total": summary.get(
                "total",
                0,
            ),

            "successful": summary.get(
                "success",
                0,
            ),

            "failed": summary.get(
                "failed",
                0,
            ),

            "skipped": summary.get(
                "skipped",
                0,
            ),

            "total_commands": summary.get(
                "total_commands",
                0,
            ),

            "execution_time": summary.get(
                "execution_time_total",
                "0.0s",
            ),
        },

        "devices": device_results,
    }


# =============================================================================
# HOME PAGE
# =============================================================================

@app.route("/")
def index():
    """
    Display NetOps Automation Suite UI.
    """

    return render_template(
        "index.html"
    )


# =============================================================================
# INVENTORY API
# =============================================================================

@app.route(
    "/api/inventory",
    methods=["GET"],
)
def get_inventory():
    """
    Return active inventory information.
    """

    try:

        devices = Inventory.load_devices()

        sites = Inventory.get_unique_values(
            devices,
            "site",
        )

        categories = Inventory.get_unique_values(
            devices,
            "category",
        )

        device_data = [
            device_to_dict(device)
            for device in devices
        ]

        return jsonify(
            {
                "success": True,

                "total": len(device_data),

                "sites": sites,

                "categories": categories,

                "devices": device_data,
            }
        )

    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


# =============================================================================
# FILTERED DEVICE API
# =============================================================================

@app.route(
    "/api/devices",
    methods=["GET"],
)
def get_devices():
    """
    Return devices filtered by Site and Category.
    """

    try:

        devices = Inventory.load_devices()

        site = request.args.get(
            "site",
            "All",
        ).strip()

        category = request.args.get(
            "category",
            "All",
        ).strip()

        filtered_devices = DeviceFilter.apply(
            devices=devices,
            site=site,
            category=category,
        )

        return jsonify(
            {
                "success": True,

                "total": len(
                    filtered_devices
                ),

                "devices": [
                    device_to_dict(device)
                    for device in filtered_devices
                ],
            }
        )

    except Exception as error:

        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


# =============================================================================
# EXECUTE OPERATION
# =============================================================================

@app.route(
    "/api/execute",
    methods=["POST"],
)
def execute_operation():
    """
    Execute Precheck, Postcheck, or Backup.
    """

    try:

        # =====================================================================
        # READ REQUEST
        # =====================================================================

        data = request.get_json(
            silent=True
        ) or {}

        operation = str(
            data.get(
                "operation",
                "",
            )
        ).strip().lower()

        site = str(
            data.get(
                "site",
                "All",
            )
        ).strip()

        category = str(
            data.get(
                "category",
                "All",
            )
        ).strip()


        # =====================================================================
        # VALIDATE OPERATION
        # =====================================================================

        valid_operations = [
            "precheck",
            "postcheck",
            "backup",
        ]

        if operation not in valid_operations:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "Invalid operation. "
                        "Choose Precheck, Postcheck, "
                        "or Backup."
                    ),
                }
            ), 400


        # =====================================================================
        # LOAD INVENTORY
        # =====================================================================

        devices = Inventory.load_devices()

        if not devices:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "No active devices found "
                        "in inventory."
                    ),
                }
            ), 400


        # =====================================================================
        # FILTER DEVICES
        # =====================================================================

        filtered_devices = DeviceFilter.apply(
            devices=devices,
            site=site,
            category=category,
        )


        # =====================================================================
        # SAFETY CHECK
        # =====================================================================

        if not filtered_devices:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "No devices matched the "
                        "selected Site and Category."
                    ),
                }
            ), 400


        # =====================================================================
        # GENERATE EXECUTION ID
        # =====================================================================

        execution_id = (
            Executor.generate_execution_id()
        )


        # =====================================================================
        # SERVER LOG
        # =====================================================================

        print()
        print("=" * 80)
        print("WEB OPERATION REQUEST")
        print("=" * 80)

        print(
            f"Execution ID : {execution_id}"
        )

        print(
            f"Operation    : {operation.upper()}"
        )

        print(
            f"Site         : {site}"
        )

        print(
            f"Category     : {category}"
        )

        print(
            f"Devices      : {len(filtered_devices)}"
        )

        print("=" * 80)


        # =====================================================================
        # EXECUTE
        # =====================================================================

        if operation == "precheck":

            results = PrecheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )

        elif operation == "postcheck":

            results = PostcheckOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )

        else:

            results = BackupOperation.run(
                devices=filtered_devices,
                site=site,
                category=category,
                execution_id=execution_id,
            )


        # =====================================================================
        # RETURN RESULT
        # =====================================================================

        response_data = build_execution_response(
            operation=operation,
            site=site,
            category=category,
            execution_id=execution_id,
            results=results,
        )

        return jsonify(
            response_data
        )


    except Exception as error:

        print()
        print("=" * 80)
        print("WEB EXECUTION ERROR")
        print("=" * 80)
        print(error)
        print("=" * 80)

        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


# =============================================================================
# RETRY FAILED DEVICES
# =============================================================================

@app.route(
    "/api/retry",
    methods=["POST"],
)
def retry_failed_devices():
    """
    Retry ONLY the failed devices from a previous execution.

    Request:

    {
        "operation": "precheck",
        "site": "LAB",
        "category": "Router",
        "execution_id": "EXEC-...",
        "failed_devices": [
            {
                "hostname": "R1",
                "ip": "192.168.122.1"
            }
        ]
    }

    Important
    ---------
    The frontend only sends device identification information.

    Device objects are ALWAYS rebuilt from the current inventory.
    """

    try:

        # =====================================================================
        # READ REQUEST
        # =====================================================================

        data = request.get_json(
            silent=True
        ) or {}

        operation = str(
            data.get(
                "operation",
                "",
            )
        ).strip().lower()

        site = str(
            data.get(
                "site",
                "All",
            )
        ).strip()

        category = str(
            data.get(
                "category",
                "All",
            )
        ).strip()

        execution_id = str(
            data.get(
                "execution_id",
                "",
            )
        ).strip()

        failed_devices_data = (
            data.get(
                "failed_devices",
                [],
            )
        )


        # =====================================================================
        # VALIDATION
        # =====================================================================

        valid_operations = [
            "precheck",
            "postcheck",
            "backup",
        ]

        if operation not in valid_operations:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "Invalid retry operation."
                    ),
                }
            ), 400


        if not execution_id:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "Execution ID is required "
                        "for retry."
                    ),
                }
            ), 400


        if not isinstance(
            failed_devices_data,
            list,
        ) or not failed_devices_data:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "No failed devices were "
                        "provided for retry."
                    ),
                }
            ), 400


        # =====================================================================
        # LOAD CURRENT INVENTORY
        # =====================================================================

        devices = Inventory.load_devices()

        if not devices:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "No active devices found "
                        "in inventory."
                    ),
                }
            ), 400


        # =====================================================================
        # BUILD FAILED IP SET
        # =====================================================================

        failed_ips = set()

        for failed_device in failed_devices_data:

            if not isinstance(
                failed_device,
                dict,
            ):
                continue

            failed_ip = str(
                failed_device.get(
                    "ip",
                    "",
                )
            ).strip()

            if failed_ip:
                failed_ips.add(
                    failed_ip
                )


        if not failed_ips:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "No valid failed device "
                        "IP addresses were provided."
                    ),
                }
            ), 400


        # =====================================================================
        # REBUILD DEVICE OBJECTS FROM INVENTORY
        # =====================================================================

        filtered_scope_devices = (
            DeviceFilter.apply(
                devices=devices,
                site=site,
                category=category,
            )
        )


        failed_devices = []

        for device in filtered_scope_devices:

            management_ip = str(
                getattr(
                    device,
                    "management_ip",
                    "",
                )
            ).strip()

            if management_ip in failed_ips:

                failed_devices.append(
                    device
                )


        # =====================================================================
        # SAFETY CHECK
        # =====================================================================

        if not failed_devices:

            return jsonify(
                {
                    "success": False,

                    "error": (
                        "Unable to map failed devices "
                        "back to the current inventory."
                    ),
                }
            ), 400


        # =====================================================================
        # SERVER LOG
        # =====================================================================

        print()
        print("=" * 80)
        print("WEB RETRY REQUEST")
        print("=" * 80)

        print(
            f"Execution ID : {execution_id}"
        )

        print(
            f"Operation    : {operation.upper()}"
        )

        print(
            f"Site         : {site}"
        )

        print(
            f"Category     : {category}"
        )

        print(
            f"Retrying     : {len(failed_devices)}"
        )

        print("=" * 80)


        # =====================================================================
        # EXECUTE RETRY
        # =====================================================================

        retry_results = Executor.execute_devices(
            devices=failed_devices,
            operation=operation,
            execution_id=execution_id,
        )


        # =====================================================================
        # RETURN RETRY RESULT
        # =====================================================================

        response_data = build_execution_response(
            operation=operation,
            site=site,
            category=category,
            execution_id=execution_id,
            results=retry_results,
        )


        # Mark response as retry
        response_data["retry"] = True

        response_data["retried_devices"] = len(
            failed_devices
        )

        return jsonify(
            response_data
        )


    except Exception as error:

        print()
        print("=" * 80)
        print("WEB RETRY ERROR")
        print("=" * 80)
        print(error)
        print("=" * 80)

        return jsonify(
            {
                "success": False,
                "error": str(error),
            }
        ), 500


# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route(
    "/api/health",
    methods=["GET"],
)
def health_check():
    """
    Application health check.
    """

    return jsonify(
        {
            "success": True,

            "application":
                "NetOps Automation Suite",

            "status":
                "Running",

            "timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
        }
    )


# =============================================================================
# APPLICATION START
# =============================================================================

if __name__ == "__main__":

    print()
    print("=" * 70)
    print(
        "NETOPS AUTOMATION SUITE"
    )
    print("=" * 70)

    print()

    print(
        "Starting Web Interface..."
    )

    print(
        "URL: http://localhost:5000"
    )

    print()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False,
    )