# -*- coding: utf-8 -*-
# añadir aqui todas las configuraciones que quiero aceptar para el modulo
# logger.

# añadir mensajes globales aqui
# no importar el modulo logger aqui

# añadir los valores por defecto.

from DTAF.config import Config
from DTAF.config.manager import ConfigEntry, ConfigSection

import logging
from logging import _STYLES, _checkLevel, _nameToLevel
import weakref
import functools
import pathlib
import os

Logger = logging.getLogger("BOOTLOADER")
g_error_msg: tuple[str] = (
    "LOG_CONFIG: Unable to load configurations",  # 0
    "LOG_CONFIG: Missing Logger Section.",  # 1
    "LOG_CONFIG: Invalid configuration. {section}::{name}::{value}",  # 2
    "LOG_CONFIG: Invalid Log Level `{level}`, please use one of the following: {levels}",  # 3
    "LOG_CONFIG: invalid path, path doesn't exists. path: {path}",  # 4
    "LOG_CONFIG: Invalid path's file extension, suffix: {suffix}, valid: {valid}",  # 5
    "LOG_CONFIG: Invalid path, path is not a directory. {path}",  # 6
    "LOG_CONFIG: Invalid path, path is not a file.",  # 7
    "LOG_CONFIG: Adding missing configuration key {key}, config: {logger_name}",  # 8
    "LOG_CONFIG: ",  # x
)
#
_log_placeholder_names: tuple[str] = (
    "name",
    "std_date",
    "usa_date",
    "id",
)
" List of valid placeholder names for the logfile's name."
_level_map = _nameToLevel
# {
#     "NOTSET": logging.NOTSET,
#     "TRACE": 9,  # USED ONLY TO DEBUG CORE, IT WILL SPAMM THE TERMINAL IF USED WITH EACH STEP.
#     "DEBUG": logging.DEBUG,
#     "INFO": logging.INFO,
#     "WARNING": logging.WARNING,
#     "ERROR": logging.ERROR,
#     "CRITICAL": logging.CRITICAL
# }
"""
Levels.

This are the levels used in logging, but are not really used. I serves just as a guide.
"""

_format_map = {
    1: "%(asctime)s - %(name)s - %(levelname) -8s - %(message)s",
    2: "%(name)s - %(levelname)s - %(asctime) -8s - %(message)s",
    3: "%(levelname)s - %(name)s - %(asctime) -8s - %(message)s",
    4: "%(name)s - %(asctime)s - %(levelname) -8s - %(message)s",
    "ROOT": "%(levelname)s - %(asctime) -8s - %(message)s",
}
"""
Formatter presets.

Formats that can be selected.
"""
_format_map_device = {
    1: "%(asctime)s - %(name)s - %(uid)s - %(levelname) -8s - %(device_class)s | %(message)s",
    2: "%(name)s - %(uid)s - %(levelname)s - %(asctime) -8s - %(device_class)s | %(message)s",
    3: "%(levelname)s - %(name)s - %(uid)s - %(asctime) -8s - %(device_class)s | %(message)s",
    4: "%(name)s - %(uid)s - %(asctime)s - %(levelname) -8s - %(device_class)s | %(message)s",
}
"""
Formatter presets for devices

Formats that can be selected when the logger for a device is added.
"""

_format_map_interface = {
    1: "%(asctime)s - %(name)s - %(duid)s - %(uid)s - %(levelname) -8s - %(interface_class)s  | %(message)s",
    2: "%(name)s - %(duid)s - %(uid)s - %(levelname)s - %(asctime) -8s - %(interface_class)s  | %(message)s",
    3: "%(levelname)s - %(name)s - %(duid)s - %(uid)s - %(asctime) -8s - %(interface_class)s  | %(message)s",
    4: "%(name)s - %(duid)s - %(uid)s - %(asctime)s - %(levelname) -8s - %(interface_class)s  | %(message)s",
}
"""
Formatter presets

Formats that can be selected when the logger for an interface is going to be used.
"""

# # añade una nueva seccion
# Config.add_section("Logger")
# # añade una nueva entrada de seccion.
# Config.add_entry("seccion", val)
# Config.add_entry("level", val)

# esto se interpreta asi:
# logger = {
#     section = val
#     level = val2
# }

# logica de carga
# verificar que exista la seccion "logger" en DTAF.config.Config
# si no existe:
#    añdir configuracion por defecto
# si existe:
#    verficar que la configuracion (nombres y valores) esten dentro de lo permitido en este archivo.

G_Section_name: str = "Logger"
initial_data: dict = {
    "default_log_level": "INFO",  # Deffault LogLevel
    "default_format": 3,
    "default_filename": "{name} - {std_date} - {id}.log",
    "max_files": 100,
    "log_dir": "~/TAF/logs/global/",
    "enable_log_files": True,
    # indica el indice de los maps de formato establecidos arriba
    "logger_config": {  # dict, store each logger level, if no present here, deffault level will be used.
        "DTAF_System": {
            "level": "INFO",
            "format": 3,
            "file_name": "{name} - {std_date} - {id}.log",
        },
        "DTAF_Devices": {
            "level": "INFO",
            "format": 3,
            "file_name": "{name} - {std_date} - {id}.log",
        },
        "DTAF_Interfaces": {
            "level": "INFO",
            "format": 3,
            "file_name": "{name} - {std_date} - {id}.log",
        },
    },
}


def add_logger_config(
    name: str = "UnamedLogger",
    level: int | str = "DEBUG",
    format: int | str = "",
    file_name: str = "{name} - {std_date} - {id}.log",
    **kwargs,
) -> bool:
    """
    Adds a new configuration to the logger_config section.

    These configurations will be used to create new logging objects
    available for DTAF.

    attributes:
        * name : str | int :: name of the logger, this will be assigned as logger.name
        * level : str | int :: logging level, see python's official documentation for logging.
        * format : str :: format string to be used, based on the modules pre-made dict, you can use your own format instead. see python's official documentation for logging for more information.
        * file_name : str :: name of the logging file, please see DTAF's Documentation to understand what fieldnames you can add. anyhting else that is not a fieldname will be interpreted as plain text.

    """
    logger_config: dict = Config.Logger.logger_config
    if name in logger_config.keys():
        raise ValueError(f"Logger Name `{name}` is already in use")
        return False
    logger_config[name] = {
        "level": level or "DEBUG",
        "file_name": file_name or "{name} - {std_date} - {id}.log",
        "format": format or 3,
    }


def _validate_logger_path(
    path: pathlib.Path | str,
    is_dir: bool = False,
    exists: bool = False,
    makedirs: bool = True,
    check_perm: bool = True,
    readable: bool = True,
    writable: bool = True,
    checkparent: bool = True,
) -> bool:
    path: pathlib.Path = pathlib.Path(path).expanduser().resolve()
    checks: tuple[bool] = (path.exists(), path.is_dir(), path.is_file())
    extensions: tuple[str] = (".log", ".txt", ".log.back", ".raw", ".info", ".debug")
    if checks[0] is False:
        Logger.debug("path doesn't exists.")
        # if it's required to exist.
        if exists is True and makedirs is False:
            Logger.critical(g_error_msg[4].format(path=path))
            raise IOError(f"file not found. file: {path}")
        # if path is dir.
        elif checks[1] is True:
            Logger.debug("path is a dir.")
            if makedirs is True:
                Logger.debug("creating parent paths as needed.")
                path.mkdir(parents=True, exist_ok=True)
        elif path.suffix not in extensions and is_dir is False:
            Logger.debug("suffix validation.")
            raise ValueError(g_error_msg[5].format(suffix=path.suffix, valid=extensions))
            # verify we have write access to it.
    # path exists.
    # path must be a directory.
    elif is_dir is True:
        Logger.debug("path is a directory.")
        # path is not a directory
        # the path is not a dir, but a file.
        if checks[1] is False or checks[2] is True:
            raise ValueError(g_error_msg[6].format(path=path))
        elif checks[1] is False and checks[2] is False:
            raise RuntimeError(f"LOG_CONFIG: Unknown state, path exists but it's neither file nor dir. path: {path}")
        # at this point the path exists
    # the path can be a file or dir, but we know it exists.
    # if we need to check access to it.
    if check_perm is True:
        check = True
        # Checks if we can read it.
        if readable is True:
            check = check and os.access(path, os.R_OK)
            Logger.debug(f"readable is required, validation: {os.access(path, os.R_OK)}")
        # Checks if we can write on it.
        if writable is True:
            check = check and os.access(path, os.W_OK)
            Logger.debug(f"writable is required, validation: {os.access(path, os.W_OK)}")
        # TODO: ADD CHECK FOR EXECUTION?
        # elif executable is True:
        #     return os.access(path, os.X_OK)
    # the path file exists
    return True


def validate_logger_config(entry: dict, logger_name: str):
    """
    Validates the logger configuration for each logger config entry.

    Attributes:

        entry: dict, contains all the basic keys and custom values. we only
        check the essential ones.

        logger_name: str; this is the name of the logger configuration we're verifying.

    """
    keys: list[str] = (
        "level",
        "file_name",
        "format",
    )
    generic_data: dict = {
        "level": "INFO",
        "file_name": "{name} - {std_date} - {id}.log",
        "format": 3,
    }
    Logger.debug(f"LOG_CONFIG: validation of logger config {logger_name}")
    for key in keys:
        if key not in entry or not entry[key]:
            Logger.warning(g_error_msg[8].format(key=key, logger_name=logger_name))
            entry[key] = generic_data[key]
        Logger.debug(f"LOG_CONFIG: validation of key {key}:`{entry[key]}`")
        match key:
            case "format":
                _STYLES["%"][0](entry[key], defaults=None)
                pass
            case "level":
                _checkLevel(entry[key])
            case "file_name":
                check: bool = _validate_logger_path(entry[key], exists=False)
                if check is not True:
                    raise RuntimeError(g_error_msg[2] +
                                       f" invalid file_name configuration. {entry[key]}, check={check}")
    return True


def check_logger_configs():
    for logger_config in Config.Logger.logger_config:
        validate_logger_config(Config.Logger.logger_config[logger_config], logger_name=logger_config)


# nos aseguramos que configuraciones tenga seccion para Logger.
if G_Section_name not in Config.sections:
    Config.add_section(G_Section_name, initial_data)

# Nos aseguramos que la seccion de configuraciones tenga la ultima versions de todas las configuraciones posibles, si no, las añade una por una.
for entry in initial_data:
    if entry not in Config.Logger.entries:
        Config.Logger.add_entry(entry, initial_data[entry])

for default_entry in initial_data:
    if default_entry != "logger_config":
        Config.Logger.add_entry(default_entry, initial_data[default_entry])
    else:
        check_logger_configs()
if (_validate_logger_path(Config.Logger.log_dir, is_dir=True, exists=False, makedirs=True, check_perm=True) is False):
    raise ValueError(g_error_msg[2].format(section="Logger", name="log_dir", value=str(Config.Logger.log_dir)))
# con esto cagamos las configuracion en memoria.
if Config.Logger.default_log_level not in _level_map:
    raise ValueError(g_error_msg[3].format(level=logging.INFO, levels=_level_map))

Config.dump(Config.filename)
