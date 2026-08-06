"""
===============================================================================
File Name   : inventory.py
Project     : NetOps Automation Suite
Description : Excel Inventory Reader
===============================================================================

Purpose
-------
This module is responsible for:

1. Finding inventory/devices.xlsx
2. Reading the Excel inventory
3. Validating required columns
4. Loading only ACTIVE devices
5. Converting Excel rows into Device objects
6. Returning unique inventory values for dynamic menus

This module DOES NOT:

- Connect to devices
- Execute commands
- Perform Precheck
- Perform Postcheck
- Perform Backup
- Generate reports

===============================================================================
"""

# Path allows us to work with files without hardcoding Windows paths.
from pathlib import Path

# pandas is used to read the Excel inventory.
import pandas as pd

# Import our Device model.
from models.device import Device


class Inventory:
    """
    Handles all Excel inventory operations.
    """

    # -------------------------------------------------------------------------
    # Required Excel Columns
    # -------------------------------------------------------------------------
    #
    # If any of these columns are missing, the application will stop and
    # clearly tell us which columns are missing.
    #
    REQUIRED_COLUMNS = [
        "Status",
        "Site",
        "Hostname",
        "Management IP",
        "Category",
        "Profile",
        "Platform",
        "OS",
        "Vendor",
        "Credential Profile",
    ]

    # -------------------------------------------------------------------------
    # Inventory File Path
    # -------------------------------------------------------------------------

    @staticmethod
    def get_inventory_file() -> Path:
        """
        Return the full path of inventory/devices.xlsx.

        Example project structure:

        NetOpsAutomationSuite/
        |
        +-- core/
        |   +-- inventory.py
        |
        +-- inventory/
            +-- devices.xlsx

        Returns
        -------
        Path
            Full path to devices.xlsx.
        """

        # __file__ points to:
        # NetOpsAutomationSuite/core/inventory.py
        current_file = Path(__file__).resolve()

        # parent = core
        # parent.parent = NetOpsAutomationSuite
        project_root = current_file.parent.parent

        # Build the inventory path.
        inventory_file = project_root / "inventory" / "devices.xlsx"

        return inventory_file

    # -------------------------------------------------------------------------
    # Validate Required Columns
    # -------------------------------------------------------------------------

    @staticmethod
    def validate_columns(dataframe: pd.DataFrame) -> None:
        """
        Validate that all required Excel columns exist.

        Parameters
        ----------
        dataframe:
            Pandas DataFrame created from devices.xlsx.

        Raises
        ------
        ValueError:
            If one or more required columns are missing.
        """

        # Compare required columns with actual Excel columns.
        missing_columns = [
            column
            for column in Inventory.REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        # Stop immediately if required columns are missing.
        if missing_columns:
            missing_text = ", ".join(missing_columns)

            raise ValueError(
                "Inventory validation failed. "
                f"Missing required column(s): {missing_text}"
            )

    # -------------------------------------------------------------------------
    # Clean Excel Cell
    # -------------------------------------------------------------------------

    @staticmethod
    def clean_value(value) -> str:
        """
        Convert an Excel cell into a clean string.

        This prevents blank Excel cells from becoming the string "nan".

        Parameters
        ----------
        value:
            Value read from Excel.

        Returns
        -------
        str
            Cleaned string value.
        """

        # If the Excel cell is empty, return an empty string.
        if pd.isna(value):
            return ""

        # Convert the value to string and remove leading/trailing spaces.
        return str(value).strip()

    # -------------------------------------------------------------------------
    # Load Devices
    # -------------------------------------------------------------------------

    @staticmethod
    def load_devices() -> list[Device]:
        """
        Read devices.xlsx and return ACTIVE devices as Device objects.

        Returns
        -------
        list[Device]
            List of active network devices.

        Raises
        ------
        FileNotFoundError:
            If devices.xlsx cannot be found.

        RuntimeError:
            If Excel cannot be read.

        ValueError:
            If required columns are missing.
        """

        # Get the inventory file location.
        inventory_file = Inventory.get_inventory_file()

        # Make sure the Excel file exists before trying to read it.
        if not inventory_file.exists():
            raise FileNotFoundError(
                "Inventory file not found:\n"
                f"{inventory_file}"
            )

        # ---------------------------------------------------------------------
        # Read Excel
        # ---------------------------------------------------------------------

        try:
            # Read the first worksheet from devices.xlsx.
            dataframe = pd.read_excel(
                inventory_file,
                engine="openpyxl"
            )

        except Exception as error:
            # Convert pandas/openpyxl errors into a cleaner application error.
            raise RuntimeError(
                "Unable to read inventory file "
                f"'{inventory_file}'. Error: {error}"
            ) from error

        # ---------------------------------------------------------------------
        # Clean Column Names
        # ---------------------------------------------------------------------

        # Removes accidental spaces such as:
        # "Hostname " -> "Hostname"
        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        # Validate Excel structure before processing devices.
        Inventory.validate_columns(dataframe)

        # ---------------------------------------------------------------------
        # Keep Only ACTIVE Devices
        # ---------------------------------------------------------------------

        # Normalize Status so all of these work:
        #
        # Active
        # ACTIVE
        # active
        # " Active "
        #
        active_mask = (
            dataframe["Status"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.casefold()
            == "active"
        )

        # Create a DataFrame containing only active devices.
        active_dataframe = dataframe.loc[active_mask].copy()

        # ---------------------------------------------------------------------
        # Convert Excel Rows into Device Objects
        # ---------------------------------------------------------------------

        devices: list[Device] = []

        # Process every active Excel row.
        for _, row in active_dataframe.iterrows():

            # Create one Device object.
            device = Device(
                status=Inventory.clean_value(row["Status"]),
                site=Inventory.clean_value(row["Site"]),
                hostname=Inventory.clean_value(row["Hostname"]),
                management_ip=Inventory.clean_value(
                    row["Management IP"]
                ),
                category=Inventory.clean_value(row["Category"]),
                profile=Inventory.clean_value(row["Profile"]),
                platform=Inventory.clean_value(row["Platform"]),
                os=Inventory.clean_value(row["OS"]),
                vendor=Inventory.clean_value(row["Vendor"]),
                credential_profile=Inventory.clean_value(
                    row["Credential Profile"]
                ),
            )

            # Add the Device object to our device list.
            devices.append(device)

        # Return all active devices.
        return devices

    # -------------------------------------------------------------------------
    # Get Unique Values
    # -------------------------------------------------------------------------

    @staticmethod
    def get_unique_values(
        devices: list[Device],
        field_name: str,
    ) -> list[str]:
        """
        Return unique values from a Device field.

        This is used to dynamically create menus.

        Examples
        --------
        Get sites:

            Inventory.get_unique_values(devices, "site")

        Result:

            ["AB", "AC", "AD"]

        Get categories:

            Inventory.get_unique_values(devices, "category")

        Result:

            ["Router", "Switch", "Wireless"]

        Parameters
        ----------
        devices:
            List of Device objects.

        field_name:
            Device attribute to inspect.

        Returns
        -------
        list[str]
            Sorted list of unique values.

        Raises
        ------
        ValueError:
            If field_name does not exist in Device.
        """

        # If there are no devices, simply return an empty list.
        if not devices:
            return []

        # Make sure the requested Device field actually exists.
        if not hasattr(devices[0], field_name):
            raise ValueError(
                f"Invalid Device field: '{field_name}'"
            )

        # Dictionary is used here to preserve the original capitalization
        # while still removing case-insensitive duplicates.
        #
        # Example:
        # Router
        # ROUTER
        # router
        #
        # will appear only once.
        unique_values: dict[str, str] = {}

        for device in devices:

            # Read the requested attribute dynamically.
            value = getattr(device, field_name)

            # Remove whitespace.
            value = str(value).strip()

            # Ignore empty values.
            if not value:
                continue

            # casefold() creates a case-insensitive comparison key.
            key = value.casefold()

            # Preserve the first real value found.
            if key not in unique_values:
                unique_values[key] = value

        # Return values alphabetically.
        return sorted(
            unique_values.values(),
            key=str.casefold
        )

    # -------------------------------------------------------------------------
    # Total Device Count
    # -------------------------------------------------------------------------

    @staticmethod
    def total_devices(devices: list[Device]) -> int:
        """
        Return total number of devices.

        Parameters
        ----------
        devices:
            List of Device objects.

        Returns
        -------
        int
            Number of devices.
        """

        return len(devices)