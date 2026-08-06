"""
===============================================================================
File Name   : profiles.py
Project     : NetOps Automation Suite
Description : Profile Loader
Author      : Prajwal Deshpande

===============================================================================

Purpose
-------
This module loads everything related to a device profile.

Example Profile

IOS_ROUTER

↓

profiles/

IOS_ROUTER/

    profile.yaml

    precheck.txt

    postcheck.txt

    backup.txt

The application never hardcodes commands.

Everything comes from these files.

===============================================================================
"""

from pathlib import Path

import yaml


class ProfileManager:
    """
    Loads Profile Information.

    Responsibilities

    ✔ Load profile.yaml

    ✔ Load precheck.txt

    ✔ Load postcheck.txt

    ✔ Load backup.txt

    ✔ Validate profile exists
    """

    # =========================================================================
    # Project Root
    # =========================================================================

    @staticmethod
    def get_profiles_directory() -> Path:
        """
        Returns

        NetOpsAutomationSuite/profiles
        """

        current_file = Path(__file__).resolve()

        project_root = current_file.parent.parent

        profiles_directory = project_root / "profiles"

        return profiles_directory

    # =========================================================================
    # Profile Folder
    # =========================================================================

    @staticmethod
    def get_profile_directory(
        profile_name: str
    ) -> Path:
        """
        Example

        IOS_ROUTER

        returns

        profiles/IOS_ROUTER
        """

        profile_directory = (
            ProfileManager.get_profiles_directory()
            / profile_name
        )

        if not profile_directory.exists():

            raise FileNotFoundError(

                f"\nProfile '{profile_name}' does not exist.\n"

                f"Expected Folder:\n"

                f"{profile_directory}"

            )

        return profile_directory

    # =========================================================================
    # Load YAML
    # =========================================================================

    @staticmethod
    def load_profile(
        profile_name: str
    ) -> dict:
        """
        Reads

        profile.yaml

        Returns

        Dictionary
        """

        profile_directory = (
            ProfileManager.get_profile_directory(
                profile_name
            )
        )

        yaml_file = (
            profile_directory /
            "profile.yaml"
        )

        if not yaml_file.exists():

            raise FileNotFoundError(

                f"profile.yaml not found.\n"

                f"{yaml_file}"

            )

        try:

            with open(

                yaml_file,

                "r",

                encoding="utf-8"

            ) as file:

                profile = yaml.safe_load(file)

        except Exception as error:

            raise RuntimeError(

                f"Unable to read\n{yaml_file}\n"

                f"{error}"

            )

        return profile

    # =========================================================================
    # Read Command File
    # =========================================================================

    @staticmethod
    def load_commands(
        profile_name: str,
        operation: str
    ) -> list[str]:
        """
        Parameters

        profile_name

            IOS_ROUTER

        operation

            precheck

            postcheck

            backup

        Returns

        List of Commands
        """

        profile_directory = (
            ProfileManager.get_profile_directory(
                profile_name
            )
        )

        command_file = (

            profile_directory /

            f"{operation.lower()}.txt"

        )

        if not command_file.exists():

            raise FileNotFoundError(

                f"\nCommand file not found.\n"

                f"{command_file}"

            )

        commands = []

        with open(

            command_file,

            "r",

            encoding="utf-8"

        ) as file:

            for line in file:

                command = line.strip()

                # Ignore Blank Lines

                if not command:

                    continue

                # Ignore Comments

                if command.startswith("#"):

                    continue

                commands.append(command)

        return commands

    # =========================================================================
    # Validate Operation
    # =========================================================================

    @staticmethod
    def validate_operation(
        operation: str
    ) -> None:
        """
        Valid Operations

        precheck

        postcheck

        backup
        """

        valid_operations = [

            "precheck",

            "postcheck",

            "backup"

        ]

        if operation.lower() not in valid_operations:

            raise ValueError(

                f"\nInvalid Operation : {operation}"

            )

    # =========================================================================
    # Get Everything
    # =========================================================================

    @staticmethod
    def load(
        profile_name: str,
        operation: str
    ) -> tuple:
        """
        Returns

        profile.yaml

        +

        commands

        Example

        profile,

        commands =

        ProfileManager.load(

            "IOS_ROUTER",

            "precheck"

        )
        """

        ProfileManager.validate_operation(
            operation
        )

        profile = (
            ProfileManager.load_profile(
                profile_name
            )
        )

        commands = (
            ProfileManager.load_commands(

                profile_name,

                operation

            )
        )

        return profile, commands