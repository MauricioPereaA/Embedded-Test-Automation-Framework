# -*- coding: utf-8 -*-
import logging
from logging import _levelToName, _nameToLevel
import weakref
import functools
import datetime
import string
import pathlib
import weakref
import os

#BOOTLOADER LOGGER:

Logger = logging.getLogger("BOOTLOADER")
Logger.setLevel(logging.DEBUG)
Logger.debug("Test Logging 0")

# only adds a file handler if we're not running on documentation mode.
import DTAF

if DTAF.SPHINX_DOC_MODE is False:
    # We only add a file handler if we're not in documentation mode.

    Logger.addHandler(
        logging.FileHandler((pathlib.Path("~/TAF/DTAF-Startup log.txt").expanduser().resolve()), mode="a"), )

Logger.warning(
    "\n\n--- Logger starts --- {dt}\n".format(dt=datetime.datetime.now().strftime("%Y-%m-%d YMD :: %Hh-%Mm-%Ss")))
#imports the logger configurations.

import DTAF.config.logger_config
from DTAF.config.logger_config import _format_map
from DTAF.config.logger_config import _format_map_device
from DTAF.config.logger_config import _format_map_interface
from DTAF.config import Config

# checks if we're running on terinal or in background.
import sys

# sets variables.
g_running_on_terminal: bool = False
# logger vars
SystemLogger: logging.Logger = None
DeviceLogger: logging.Logger = None
InterfaceLogger: logging.Logger = None

if sys.stdin and len(os.getenv('PSModulePath', '').split(os.pathsep)) >= 3:
    g_running_on_terminal = True

Logger.info(f"Running on terminal: {g_running_on_terminal}")

# Set Globals #
#--------------

g_error_msg: tuple[str] = (
    "Logger: Logger Name already in use. Logname: `{logname}`",  # 0
    "Logger: Logger Name not found. Logname: `{logname}`",  # 1
    "Logger: Missing Logger Level Configuration entry, using global level: [{level}]",  # 2
    "Logger: Invalid Log Level `{level}`, please use one of the following: {levels}",  # 3
    "Logger: Configuration Error, the configuration `{conf_name}`. {conf_msg}",  # 4
    "Logger: invalid format key, logger `{logger_name}` uses the key index [{index}], while the valid keys are {keys}",  # 5
    "Logger: Invalid format stringg, missing `%` format parametters. format: `{ftm}`",  # 6
    "Logger: ",  # x
)
"""
Global Error message pointer.
"""

g_warning_msg: tuple[str] = (
    "Logger: Programm is running without a console.",  # 0
    "Logger: Missing format field name: {fname}",  # 1
    "Logger: Invalid `log_dir` value; it's a file, using parent path instead. value: `{path}`",  # 2
    "Logger: New folder has been assigned as logging file home, creating parents if necessary. path: `{path}`",  # 3
    "Logger: ",  # x
)
"""
Global Warning Message pointer.
"""

_handlers = {}
"""
Relationship between handlers and names.
"""

#Loggers created are going to be stored here
global_logger_list = dict()
"""
Global logger list.

Used to store all the loggers created globally.
"""


def trace(self, message, *args, **kws):
    """
    Trace function.

    Method where you add a message with the trace prefix.
    """
    self._log(9, message, args, **kws)


def add_trace_level():
    """
    Trace level adder.

    Adds the trace level to logging and relates the trace() method with the
    trace level.
    """
    if "TRACE" not in _nameToLevel:
        logging.addLevelName(9, "TRACE")
    if hasattr(logging.Logger, "trace") is False:
        logging.Logger.trace = trace


if "TRACE" not in _nameToLevel:
    add_trace_level()
#MO
# ROOT LOGGER:
# |-> Device Logger
#     Each interface will have it's own logger where they will display their
#     UID, and a human redeable title to make easy for us to understand what
#     did log the message
#     |-> Interface Logger
#         Each interface will have their own spawn of a logger managing their log
#         messages in the squence [uid:device_id: interface_name]. this will
#         allow the user to understan which interface did what.
# |-> System Logger
#     Each module will have it's own logger instance.
#     |-> Builder Module
#         example: "Builder: failed to load model scheme at 323 from ../model.yaml"
# this information is for developers only.

_format_colors = {
    "INFO": '\033[32m',  #GREEN
    "WARNING": '\033[33m',  #YELLOW
    "ERROR": '\033[47;31m',  #RED
    "CRITICAL": '\033[31m',  #ORANGE
    "TRACE": '\033[36m',  #CYAN
    "DEBUG": '\033[34m'  #BLUE
}
"""
Format colors by level.

Colors for each logging level in ANSI code.
"""

g_clear_format_code = '\033[0m'
"""
Clear code.

Code in ANSI used to mark an escape character.
"""


# MO
# format logger:
# the format logger will emmit the messages to the root logger without any
# format while it will parse a formatted version to the terminal logger
#
class color_format(logging.Formatter):
    """
    Color the levelname.

    inherits from formatter and overrides format so that you can color to the section
    where the levelname appears.
    """

    def format(self, record) -> logging.LogRecord:
        """
        Levelname reformat.

        Changes what is inside record.levelname so that it can have color.
        It adds the ANSI codes to the front and back of levelname and returns it.
        """
        record.levelname = f"{_format_colors.get(record.levelname)}{record.levelname}{g_clear_format_code}"
        return super().format(record)


# el root logger no contrendra caracteres especiales, unicamente la informacion base,
# ex:ERROR : TIME_MARK : MSG

# el format logger emitira la informacion al terminal logger para que se muestre
# en colores el resumen y las pruebas enviadas a sys.stdout y sys.stedrr

# el modulo logger.py debe ser capaz de identificar cuando el programa se inicia
# con terminal activa o no, y asi evitar cargar los handlers en los loggers cuando sea innecesario.


#Add the name of the logger created to the _global_logger_list dictionary
def add_log_reg(logname: str, ref: weakref):
    """
    Add logger to register.

    Adds logger to a global list that will keep track of all the loggers created.
    If not it throws an error.
    """
    if logname not in global_logger_list:
        global_logger_list[logname] = ref
        return True
    else:
        raise RuntimeError(g_error_msg[0].format(logname=logname))


#Delete logger from __global_logger_list
def erase_log_reg(logname: str):
    """
    Delete logger from __global_logger_list.

    Deletes the registry of a previously entered logger. If it is not found it
    throws an error.
    """
    if logname in global_logger_list:
        del global_logger_list[logname]
        return True
    else:
        raise RuntimeError(g_error_msg[1].format(logname=logname))


#Creates the log objects
def create_logger(logname: str, level: str):
    """
    Create a logger.

    creates a logger object with the name you specified, assigns a level to it,
    creates a weak reference to it, adds it to the global logger dictionary and
    returns the logger that was created.
    """
    log = logging.getLogger(logname)
    log.setLevel(level)
    ref = weakref.ref(log)
    add_log_reg(logname, ref)
    return log


#Deletes specified logger
def del_logger(logname: str):
    """
    Deletes logger.

    Deletes specified logger object from the loggerdict.
    """
    return logging.Logger.manager.loggerDict.pop(logname, None)


#Configures a terminal handler
def config_terminal_handler(frmt: str) -> logging.StreamHandler:
    """
    Terminal handler.

    This will create a console handler that will format the message with the
    format selected and it will add color to the level of the warning. The handler
    is returned to be used by add_handler.
    """
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(color_format(frmt))
    return console_handler


def format_filename(**kwargs: dict) -> str:
    """
    Formats the filename based on the pressence of the different supported key
    name fields.

    Argumests:
        name: name of the logger as in the config file.
        filename: str : name of the file, with the format placeholders.
        date: datetime.datetime : datetime object to use as source for the strftime method.
        id: int : Numeric ID of the file iteration. it will be based on the sum of al the files in the folder.
        * custom arguments: typing.any : Add any argument as you desire to parse methods to contorl and format the source. use functools.partial or lamda functions.

    Supported keyfields:
        * name : keyname of the logger as it appears in the configuration file.
        * std_date : Standard date format (ISO) YYYY-MM-DD - HH-MM-SS.
        * usa_date : USA time format MM-DD-YYYY - HH-MM-SS.
        * id : Iteration name in the logging folder.
    """
    filename: str = kwargs.get("filename", Config.Logger.default_filename)
    # retrieves the date from the argument list.
    date = kwargs.get("date", datetime.datetime.now())
    if isinstance(date, datetime.datetime) is False:
        date = datetime.datetime.now()

    format_keys: list[str] = [n[1] for n in string.Formatter().parse(filename) if n[1]]
    Logger.debug(f"Analized filename: {filename}, argumenst: {format_keys}")

    #
    class Default_format_dictionary(dict):

        def __missing__(self, key: str) -> str:
            Logger.warning(g_warning_msg[1].format(fname=key))
            return lambda *x: key

    format_dict: dict = Default_format_dictionary({
        "std_date": functools.partial(date.strftime, "%Y-%m-%d %H-%M-%S"),
        "usa_date": functools.partial(date.strftime, "%m-%d-%Y %H-%M-%S"),
        "id": functools.partial(kwargs.get, "id", "0"),
        "name": functools.partial(kwargs.get, "name", "Unamed_Logger"),
    }
                                                  # TODO: ADD ID ASSIGNATION METHOD
                                                  )
    Logger.debug(f"Logger: filename = `{filename}`")
    buffer: dict = {}
    for key in format_keys:
        buffer[key] = format_dict.get(key, "key")()
        #Logger.debug(f"Logger: key: `{key}`, buffer[key]: `{buffer[key]}`")

    # filename = filename.format_map({key:format_dict[key] for key in format_keys})
    filename = filename.format_map(buffer)
    Logger.debug(f"Logger: filename = `{filename}`\n")
    return filename


#configures a file handler
def config_file_handler(lggr: logging.Logger, frmt: str, name: str = '', mode: str = 'w'):
    """
    File Handler.

    This will create a file handler that will write all the logs into a file with the name of
    your logger and sets the logger for it. The handler is formatted with the
    format given and then returned to be used by add_handler.
    """
    path: pathlib.Path = pathlib.Path(Config.Logger.log_dir).expanduser().resolve()
    Logger.debug(f"Currently working at path: `{path}`")
    checks: list[bool] = [path.exists(), path.is_dir()]
    log_handler: logging.FileHandler = None
    # configs the directory path.
    if False in checks:
        if checks[0] is True:
            path = path.parent
            Logger.warning(g_warning_msg[2].format(path=path.parent))
        else:
            path.mkdir(parents=True, exist_ok=True)
            Logger.warning(g_warning_msg[3].format(path=path))
    if name:
        log_handler = logging.FileHandler(str(path / name), mode=mode)
    # adds the file handler
    else:
        log_handler = logging.FileHandler(str(path / str(lggr.name)) + '.log', mode=mode)
    if not log_handler:
        raise RuntimeError(g_error_msg[7].format(logger=lggr.name))
    log_handler.setFormatter(logging.Formatter(frmt))
    return log_handler


#Method that adds a handler to a certain logger
def add_handler(logger: logging.Logger,
                hndlrtype: str,
                frmt: str,
                filename: str = '',
                mode: str = 'w') -> logging.Handler:
    """
    Handler adder.

    Takes a handler type, gives the one you need formatted accordingly to the format
    you want(you can check the predetermined formats in logger_config.py(_format_map))
    and adds it to a logger.

    returns the handler.
    """
    added = False
    hndlr = None
    Logger.debug(
        f"executing add_handler - logger: `{logger.name}`, hndlrtype: `{hndlrtype}`, frmt: `{frmt}`, filename: `{filename}`"
    )
    logger_name: str = logger.name
    if logger_name not in _handlers:
        _handlers[logger_name[:]] = {"logger": weakref.ref(logger, lambda *x: _handlers.pop(logger_name[:]))}
    match hndlrtype:
        case "Terminal":
            Logger.debug("Logger: adding new handler. type:`Terminal`.")
            hndlr = config_terminal_handler(frmt)
            added = True
            _handlers[logger_name[:]]["Terminal"] = weakref.ref(hndlr,
                                                                lambda *x: _handlers[logger_name[:]].pop("Terminal"))
        case "File":
            Logger.debug("Logger: adding new handler. type:`File`.")
            hndlr = config_file_handler(logger, frmt, name=filename, mode=mode)
            added = True
            _handlers[logger_name[:]]["File"] = weakref.ref(hndlr, lambda *x: _handlers[logger_name[:]].pop("File"))
    if hndlr:
        logger.addHandler(hndlr)
    return hndlr


def get_handlers(logger_name: str) -> dict:
    """
    returns a relationship between loggers and hanlders ordered by logger.name
    """
    return _handlers.get(logger_name)


#TODO: CREATE REPORT FORMAT BASED ON PYTEST'S FORMAT AND USE DTAF'S
# CONFIGURATION MODULE TO DETERMINE WHERE TO PUT IT OR WHERE TO SEND IT.
#class TestReport():
#   Replicar lo de estos comandos en los formatos que se pidan
#    python -m pytest TestingSeq.py --html=report.html
#    python -m pytest TestingSeq.py -q --excelreport=report.xls
#    python -m pytest TestingSeq.py --junitxml=result.xml
#    para hacer formatos de los resultados de tests
#    pass
# TODO: TEST LIVE UPDATES ON THE LOG LEVEL AND HANDLERS ON THE TEST FILE, format, nivel, nombre archivo, limite de archivos, carpeta de trabajo
# Creates a log for each device, use this one when a new device is added

#TODO: add a way to incorporate a uid to each device and interface.

# Configure the Default Loggers.
# ------------------------------

#adds the hendlers as needed.

default_config: dict = {
    "level": Config.Logger.default_log_level,
    "format": 3,
    "file_name": "{name} - {std_date} - {id}.log",
    "DTAF_System": _format_map,
    "DTAF_Devices": _format_map_device,
    "DTAF_Interfaces": _format_map_interface,
}


def __raise_config_error(config: str, msg_: str):
    msg: str = g_error_msg[4].format(
        conf_name=config,
        conf_msg=msg_,
    )
    raise ValueError(msg)


# Checks the config.
if isinstance(Config.Logger.default_format, int):
    default_config["format"]: _format_map[Config.Logger.default_format]
#
elif isinstance(Config.Logger.default_format, str):
    if "%" not in Config.Logger.default_format:
        __raise_config_error(
            default_config["format"],
            "The format configuration string must have at least a placeholder, missing %",
        )
    default_config["format"]: Config.Logger.default_format
#
else:
    __raise_config_error(
        "default_format",
        "Config must be an integer in the [0-{}] range; or a logging string format. please see `https://docs.python.org/3/library/logging.html#logrecord-attributes` for more information."
        .format(len(_format_map) - 1))


@functools.singledispatch
def get_format(index: int, source: dict = {}, source_name: str = '') -> str:
    if index not in source:
        raise ValueError(g_error_msg[5].format(logger_name=source_name, index=index, keys=source.keys()))
    return source[index]


@get_format.register(str)
def _(index: str, source: list[str] = [""], source_name: str = '') -> str:
    # gets the
    if "%" not in index:
        raise ValueError(g_error_msg[6].format(ftm=index))
    return index


def set_console_handler(logger: logging.Logger, format_string: int | str = 0) -> None:
    """
    Verifies that we're running in a shell otherwise it will log a simple warning.
    """
    handler: logging.Handler = None
    if sys.stdin:
        if sys.stdin.isatty():
            handler = add_handler(logger, "Terminal", get_format(format_string))
            return handler
    else:
        Logger.warning(g_warning_msg[0])
    return None


#
def _load_default_loggers():
    # set variables.
    global SystemLogger, DeviceLogger, InterfaceLogger
    default_log_level: str = Config.Logger.default_log_level
    logger_names: list[str] = ["DTAF_System", "DTAF_Devices", "DTAF_Interfaces"]
    logger_name: str = ''
    filename: str = ''
    log_config: dict = Config.Logger.logger_config
    handler: logging.Handler = None
    cc: int = 0
    # Iter over log names
    # for logger_name in logger_names:
    #     if logger_name not in Config.Logger.logger_config:
    #         Logger.warning(g_error_msg[2].format(default_log_level))
    #     log_level = Config.Logger.logger_config.get(logger_name, Config.Logger.log_level)
    #     log_config[logger_name] = log_level
    #     Logger.debug(f"logger_name: {logger_name}; log_level: {log_level}")

    # Configures the deffault Loggers.
    SystemLogger = create_logger(logger_names[0], log_config[logger_names[0]]["level"])
    DeviceLogger = create_logger(logger_names[1], log_config[logger_names[1]]["level"])
    InterfaceLogger = create_logger(logger_names[2], log_config[logger_names[2]]["level"])

    # Sends debug message.
    logger_name = None
    Logger.debug(f"log_config: {log_config}")
    Logger.debug(f"logger_names: {logger_names}")
    # lists loggers
    default_loggers = (
        SystemLogger,
        DeviceLogger,
        InterfaceLogger,
    )
    # configures extra handlers.
    cc = 0
    for logger_instance in default_loggers:
        logger_name = logger_names[cc]
        Logger.debug(f"Logger: Setting Logger [{logger_instance}] for {logger_name} console handler.")
        # gest the config.
        config = Config.Logger.logger_config.get(logger_name, default_config)
        format = get_format(config.get("format", default_config.get("format", None)),
                            source=default_config[logger_name],
                            source_name=logger_name)
        # sets logger level.
        log_level = config.get("level", logging.WARNING)
        logger_instance.setLevel(log_level)
        # Checks we're not in sphinx doc mode.
        if DTAF.SPHINX_DOC_MODE is False:
            # adds the file handler.
            Logger.debug(f"config: {config}, format: {format}, filename = {filename}")
            filename = format_filename(filename=config.get("file_name", "{name} - {std_date} - {id}.log"),
                                       name=logger_instance.name)
            handler = add_handler(logger_instance, "File", format, filename=filename)
            handler.setLevel(log_level)
        # Sets console handler if program is ran in console.
        handler = set_console_handler(logger_instance, format)
        if handler:
            handler.setLevel(log_level)
        Logger.debug(f"logger: {logger_instance.name}, handlers: {logger_instance.handlers}")
        cc += 1
    cc = None


def __init__():
    global Logger
    Logger.debug("Loading __init__ from DTAF.logger")
    _load_default_loggers()
    Logger = SystemLogger


__init__()
