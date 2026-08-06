"""
===============================================================================
File Name   : credentials.py
Project     : NetOps Automation Suite
Description : Credential Manager
Author      : Prajwal Deshpande

===============================================================================

Purpose
-------

Responsible for reading credentials.yaml.

Example:

Device
------
Credential Profile = TACACS

↓

credentials.yaml

↓

username

password

secret

↓

Return credentials to Netmiko

===============================================================================
"""

# =============================================================================
# Imports
# =============================================================================

from pathlib import Path

import yaml


# =============================================================================
# Credential Manager
# =============================================================================

class CredentialManager:
    """
    Handles all credential related operations.
    """

    # -------------------------------------------------------------------------
    # Credential File
    # -------------------------------------------------------------------------

    @staticmethod
    def get_credential_file() -> Path:
        """
        Returns

        config/credentials.yaml
        """

        current_file = Path(__file__).resolve()

        project_root = current_file.parent.parent

        credential_file = (
            project_root
            / "config"
            / "credentials.yaml"
        )

        return credential_file

    # -------------------------------------------------------------------------
    # Read YAML
    # -------------------------------------------------------------------------

    @staticmethod
    def load_credentials() -> dict:
        """
        Reads credentials.yaml.

        Returns
        -------
        dict
        """

        credential_file = (
            CredentialManager.get_credential_file()
        )

        if not credential_file.exists():

            raise FileNotFoundError(

                f"\ncredentials.yaml not found.\n"

                f"{credential_file}"

            )

        try:

            with open(

                credential_file,

                "r",

                encoding="utf-8"

            ) as file:

                credentials = yaml.safe_load(file)

        except Exception as error:

            raise RuntimeError(

                f"\nUnable to read credentials.yaml\n"

                f"{error}"

            )

        if credentials is None:

            raise RuntimeError(

                "credentials.yaml is empty."

            )

        return credentials

    # -------------------------------------------------------------------------
    # Get Credential Profile
    # -------------------------------------------------------------------------

    @staticmethod
    def get_profile(
        credential_profile: str
    ) -> dict:
        """
        Returns one credential profile.

        Example

        TACACS

        Returns

        {
            username,
            password,
            secret
        }
        """

        credentials = (
            CredentialManager.load_credentials()
        )

        if credential_profile not in credentials:

            raise ValueError(

                f"\nCredential Profile "

                f"'{credential_profile}' "

                f"not found."

            )

        profile = credentials[credential_profile]

        # Validate required keys

        required = [

            "username",

            "password",

            "secret"

        ]

        for key in required:

            if key not in profile:

                raise ValueError(

                    f"\nMissing '{key}' "

                    f"in credential profile "

                    f"{credential_profile}"

                )

        return profile

    # -------------------------------------------------------------------------
    # Get Username
    # -------------------------------------------------------------------------

    @staticmethod
    def username(
        credential_profile: str
    ) -> str:

        profile = CredentialManager.get_profile(
            credential_profile
        )

        return profile["username"]

    # -------------------------------------------------------------------------
    # Get Password
    # -------------------------------------------------------------------------

    @staticmethod
    def password(
        credential_profile: str
    ) -> str:

        profile = CredentialManager.get_profile(
            credential_profile
        )

        return profile["password"]

    # -------------------------------------------------------------------------
    # Get Enable Secret
    # -------------------------------------------------------------------------

    @staticmethod
    def secret(
        credential_profile: str
    ) -> str:

        profile = CredentialManager.get_profile(
            credential_profile
        )

        return profile["secret"]