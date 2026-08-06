"""
===============================================================================
File Name   : connection.py
Project     : NetOps Automation Suite
Author      : Prajwal Deshpande

Description
-----------
This module is responsible for establishing SSH connections to network devices
using Netmiko.

Responsibilities
----------------
✔ Read profile settings
✔ Read credentials
✔ Build Netmiko connection parameters
✔ Connect to device
✔ Enter enable mode (if required)
✔ Disable terminal paging
✔ Return active SSH connection

This module DOES NOT
--------------------
❌ Execute Precheck
❌ Execute Postcheck
❌ Execute Backup
❌ Generate Reports

===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

# Netmiko connection library
from netmiko import ConnectHandler

# Netmiko Exceptions
from netmiko.exceptions import (
    NetmikoAuthenticationException,
    NetmikoTimeoutException,
)

# General SSH Exception
from paramiko.ssh_exception import SSHException

# Import Device Model
from models.device import Device

# Import Profile Loader
from core.profiles import ProfileManager

# Import Credential Loader
from core.credentials import CredentialManager


# =============================================================================
# Connection Manager
# =============================================================================

class ConnectionManager:
    """
    Handles SSH Connections.

    Example
    -------

    connection = ConnectionManager.connect(device)

    connection.send_command("show version")

    connection.disconnect()
    """

    # =========================================================================
    # Build Netmiko Parameters
    # =========================================================================

    @staticmethod
    def build_connection_parameters(
        device: Device
    ) -> dict:
        """
        Build Netmiko connection dictionary.

        Parameters
        ----------
        device : Device

        Returns
        -------
        dict
            Dictionary accepted by Netmiko ConnectHandler().
        """

        # --------------------------------------------------------------
        # Load Profile
        # --------------------------------------------------------------

        profile = ProfileManager.load_profile(
            device.profile
        )

        # --------------------------------------------------------------
        # Load Credentials
        # --------------------------------------------------------------

        credentials = CredentialManager.get_profile(
            device.credential_profile
        )

        # --------------------------------------------------------------
        # Build Dictionary
        # --------------------------------------------------------------

        connection_parameters = {

            # Device IP Address
            "host": device.management_ip,

            # Username
            "username": credentials["username"],

            # Password
            "password": credentials["password"],

            # Enable Secret
            "secret": credentials["secret"],

            # Netmiko Device Type
            "device_type": profile["device_type"],

            # Connection Timeout
            "timeout": profile.get(
                "timeout",
                120
            ),

            # Fast CLI
            "fast_cli": profile.get(
                "fast_cli",
                False
            ),

            # Delay Factor
            "global_delay_factor": profile.get(
                "global_delay_factor",
                1
            ),

        }

        return connection_parameters

    # =========================================================================
    # Connect
    # =========================================================================

    @staticmethod
    def connect(
        device: Device
    ):
        """
        Connect to a network device.

        Parameters
        ----------
        device : Device

        Returns
        -------
        Netmiko Connection Object
        """

        # --------------------------------------------------------------
        # Build Netmiko Dictionary
        # --------------------------------------------------------------

        connection_parameters = (
            ConnectionManager.build_connection_parameters(
                device
            )
        )

        try:

            # ----------------------------------------------------------
            # SSH Login
            # ----------------------------------------------------------

            connection = ConnectHandler(
                **connection_parameters
            )

            # ----------------------------------------------------------
            # Load Profile
            # ----------------------------------------------------------

            profile = ProfileManager.load_profile(
                device.profile
            )

            # ----------------------------------------------------------
            # Enter Enable Mode
            # ----------------------------------------------------------

            if profile.get(
                "enable",
                False
            ):

                connection.enable()

            # ----------------------------------------------------------
            # Disable Paging
            # ----------------------------------------------------------

            paging_command = profile.get(
                "paging_disable"
            )

            if paging_command:

                connection.send_command_timing(
                    paging_command
                )

            # ----------------------------------------------------------
            # Connection Successful
            # ----------------------------------------------------------

            return connection

        # ----------------------------------------------------------
        # Authentication Error
        # ----------------------------------------------------------

        except NetmikoAuthenticationException as error:

            raise ConnectionError(

                f"\nAuthentication Failed\n\n"

                f"Hostname : {device.hostname}\n"

                f"IP       : {device.management_ip}\n\n"

                f"{error}"

            )

        # ----------------------------------------------------------
        # Timeout Error
        # ----------------------------------------------------------

        except NetmikoTimeoutException as error:

            raise TimeoutError(

                f"\nConnection Timeout\n\n"

                f"Hostname : {device.hostname}\n"

                f"IP       : {device.management_ip}\n\n"

                f"{error}"

            )

        # ----------------------------------------------------------
        # SSH Error
        # ----------------------------------------------------------

        except SSHException as error:

            raise ConnectionError(

                f"\nSSH Error\n\n"

                f"Hostname : {device.hostname}\n"

                f"IP       : {device.management_ip}\n\n"

                f"{error}"

            )

        # ----------------------------------------------------------
        # Unknown Error
        # ----------------------------------------------------------

        except Exception as error:

            raise RuntimeError(

                f"\nUnexpected Error while connecting\n\n"

                f"Hostname : {device.hostname}\n"

                f"IP       : {device.management_ip}\n\n"

                f"{error}"

            )

    # =========================================================================
    # Execute Single Command
    # =========================================================================

    @staticmethod
    def execute_command(
        connection,
        command: str
    ) -> str:
        """
        Execute one command.

        Parameters
        ----------
        connection
            Active Netmiko connection.

        command
            Command to execute.

        Returns
        -------
        str
            Device output.
        """

        output = connection.send_command(

            command,

            expect_string=None,

            read_timeout=120

        )

        return output

    # =========================================================================
    # Execute Multiple Commands
    # =========================================================================

    @staticmethod
    def execute_commands(
        connection,
        commands: list[str]
    ) -> dict:
        """
        Execute multiple commands.

        Parameters
        ----------
        connection

        commands

        Returns
        -------
        dict

        Example

        {

            "show version": "...",

            "show inventory": "...",

            "show interfaces": "..."

        }
        """

        outputs = {}

        for command in commands:

            output = (

                ConnectionManager.execute_command(

                    connection,

                    command

                )

            )

            outputs[command] = output

        return outputs

    # =========================================================================
    # Disconnect
    # =========================================================================

    @staticmethod
    def disconnect(
        connection
    ) -> None:
        """
        Disconnect safely.

        Nothing happens if connection
        is already closed.
        """

        if connection:

            try:

                connection.disconnect()

            except Exception:

                pass

    # =========================================================================
    # Test Connection
    # =========================================================================

    @staticmethod
    def test_connection(
        device: Device
    ) -> bool:
        """
        Tests whether SSH login works.

        Returns
        -------
        True

        False
        """

        connection = None

        try:

            connection = (

                ConnectionManager.connect(

                    device

                )

            )

            return True

        except Exception:

            return False

        finally:

            ConnectionManager.disconnect(

                connection

            )