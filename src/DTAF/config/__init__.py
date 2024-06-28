# -*- coding: utf-8 -*-
from DTAF.config.manager import ConfigManager
import platform
import pathlib

Config: ConfigManager = None
"""
Configuration Object.

This object will store all configurations loaded from
the file parsed down.
"""

HOMEDIR: pathlib.Path = None


def load_essential() -> None:
    """
    Loads the essential modules and configurations.

    This method will contain all instructions for the module to load correctly
    and for us to be able to track any issue that may happen
    """
    pass


def get_user_space() -> pathlib.Path:
    """
    Gets the user space to store configuration and files akin
    """
    platform_name: str = platform.uname().system
    # Gets user space
    user_path: pathlib.Path = pathlib.Path().home()

    # checks or creates configuration dir.
    if platform_name == "Windows":
        user_path = user_path / "TAF" / "DTAF"
    elif platform_name == "Linux":
        user_path = user_path / ".TAF" / "DTAF"
    elif platform_name == "Darwin":
        user_path = user_path / "Library" / "Preferemces" / ".TAF" / "DTAF"

    # Tries to create the full path.
    user_path.mkdir(parents=True, exist_ok=True)
    return user_path


def load_globals() -> None:
    """
    Static Method to load all globals in memory.
    """
    global Config, HOMEDIR
    HOMEDIR = get_user_space()
    _config_path = HOMEDIR / "config.toml"
    Config = ConfigManager(filename=_config_path)
    Config.dump(_config_path)
    pass


load_globals()

# Cargamos Configuraciones del logger.
import DTAF.config.logger_config
