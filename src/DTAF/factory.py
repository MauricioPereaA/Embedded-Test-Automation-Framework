# -*- coding: utf-8 -*-
# General imports.
import pathlib
import importlib
import typing

# DTAF Specific imports
from DTAF.config import Config
from DTAF.interfaces.interfaces import InterfaceBase
from DTAF.devices.device import DeviceBase

import threading

# Temporal Logger.
import logging

Logger = logging.getLogger("Factory")

# Default working dir: ~/TAF/DTAF/General
G_user_dir: pathlib.Path = pathlib.Path("~/TAF/DTAF/99-General").expanduser()
# Tries to access default working dir
if G_user_dir.exists() is False:
    try:
        G_user_dir.mkdir(parents=True)
    except Exception:
        Logger.exception("Unable to create/access User resources path: {}".format(G_user_dir))
# Get config section for factory discovery.

g_warning_msg: tuple[str] = (
    "Factory: Object Registry [{name}] updated, all new instances will use {cls} as base.",  # x
    "Factory: ",  # x
)
"""
List of warning messages.
"""

g_error_msg: tuple[str] = (
    "Factory: Object Name is already in use.  name:{name},  cls:{cls},  new:{original}",  # 0
    "Factory: Can't update Object in memory, The name is not present in memory. name: {name}, cls: {cls}",  # 1
    "Factory: This feature is not implemented yet. {msg}.",  # 2
    "Factory: Invalid name, there is no registry by the name of {name}.",  # 3
    "Factory: There can only be one instance of the factory. Use DTAF.interface.factory.Factory instead.",  # 4
    "Factory: Invalid class to register in builder.",  # 5
    "Factory: Invalid Attribute Name. not found in registry. Name: {name}.",  # 6
    "Factory: Invalid Class Type, the class is not related to DTAF's Base Classes. Class-type: {type_}, Class:{cls}.",  # 7
    "Factory: Unregistered class. class provided couldn't be found in registry. cls: {cls}.",  # 8
    "Factory: Invalid Class Type, This class doesn't share root with DTAF's Base classes. name: {name}, Class:{cls}.",  # 9
    "Factory: ",  # x
)
"""
List of error messages.
"""

g_info_msg: tuple[str] = (
    "Factory: Created main factory instance.",  # 0
    "Factory: ",  # x
)
"""
List of info messages.
"""


class _Factory:
    __store: dict = {}
    """
    Storage area.

    Here we store all the information in memory.
    """

    def class_finder(self, class_str: str, class_name: str):
        """
        this method will allow you to load new classes by using their import
        method rather than to import the lib before calling the method.

        the idea is that the end user will be able to call method that are not
        in the global __import__ scope, so the factory can load them later on
        and avoid cycling importation.

        This method is experimental.

        usage:
        factory_instance.register("name", "path.of.the.module.name")

        This will then use class finder to find the name of the object inside
        the module, first by trying to import the whole name using import lib
        and then requesting the name as an attribute.

        we will load the module name into the global __import__ scope and use
        the whole name to refer to the object in memory.

        which means, we would use "path.of.the.module.name" instead of just the
        name of the object.
        """
        _object: InterfaceBase | DeviceBase = None
        lib = None
        try:
            lib = importlib.import_module(class_str)
        except ModuleNotFoundError as error:
            Logger.exception(f"Factory: couldn't find the module {class_str}", error)
            try:
                _class_str = ".".join(class_str.split(".")[:-1])
                if _class_str:
                    lib = self.class_finder(_class_str)
                else:
                    raise ModuleNotFoundError("Factory: No parent module found")
            except ModuleNotFoundError as error:
                Logger.exception(f"Factory: couldn't find parent from the module path given: {_class_str}", error)
                raise
        # here we could load the module in memory.
        if hasattr(lib, class_name):
            _object = getattr(lib, class_name)
            if issubclass(_object, (DeviceBase, InterfaceBase)) is False:
                raise ImportError(f"Factory: Object {class_name}:{_object} from {class_str} "
                                  "is neither a [`DeviceBase` or `InterfaceBase`] subclass.")
        else:
            raise ImportError(f"Factory: Module {class_str} "
                              f"doens't have any attribute nor Object named `{class_name}`")
        return _object

    @property
    def classnames(self, ) -> list[str]:
        """
        List of all registered class names.

        Returns a list of valid class names as strings.
        """
        return list(self.__store.keys())

    __store_lock: threading.Lock = threading.Lock()
    """
    Storage Block.

    This lock will allow us to make thread safe transactions.
    """

    _flag_instance: bool = False

    def __init__(self) -> None:
        Logger.info(g_info_msg[0])
        if _Factory._flag_instance is True:
            raise RuntimeError(g_error_msg[4])
        _Factory._flag_instance = True

    def register(self, name: str, cls: object) -> bool:
        """
        Registers a new namespace in memory from the classes given.

        :param str name: Name of the object to register as key.
        :param object cls: Class definition of the Object.
        """
        with self.__store_lock:
            # checks the name is already in use.
            if name in self.__store:
                raise ValueError(g_error_msg[0].format(name=name, cls=cls, original=self.__store.get(name, None)))
            # Verifies that it's a valid object
            # TODO: Add verification process here.
            if isinstance(cls, str):
                result = self.class_finder(name, cls)
            else:
                result = self.verify_class(cls)
            if result is False:
                raise RuntimeError(g_error_msg[5])
            # registers the name in memory.
            self.__store[name] = cls
            Logger.info(f"Factory: bound {name} to {cls}")
            return True

    def unregister(self, name: str) -> bool:
        """
        Removes a namespace from memory.

        Remobes the store of the name from memory.

        :param str name: Name of the class to un-register.

        .. warning::
            All instances created prior to the change will stay the same as they
            where created.
        """
        with self.__store_lock:
            if name in self.__store:
                del self.__store[name]
                return True
            raise NameError(g_error_msg[3].format(name=name))
        return False

    def update_definition(self, name: str, cls: object) -> None:
        """
        Updates the object definition.

        Updates the object class definition with the newer version.

        :param str name: Name of the object in registry.
        :param object cls: Class definition.

        .. warning::
            All instances created prior to the change will stay the same as they
            where created.
        """
        if issubclass(cls, (DeviceBase, InterfaceBase)):
            raise RuntimeError(g_error_msg[9].format(name=name, cls=cls))
        if name not in self.__store:
            raise RuntimeError(g_error_msg[1].format(name=name, cls=cls))
        Logger.warning(g_warning_msg[0].format(name=name, cls=cls))
        self.__store[name] = cls

    def verify_class(self, cls: object) -> bool:
        """
        Validates the class provided.

        Verify that the cls parameter is a subclass/instance of DeviceBase.

        :param object cls: Class to be verified.
        """
        result: bool = False
        result = issubclass(cls, (DeviceBase, InterfaceBase))
        # raise NotImplementedError(g_error_msg[2].format("; Missing class definition validation"))
        if result is True:
            return result
        raise TypeError(g_error_msg[7].format(type_=type(cls), cls=cls))
        return result

    def __getattr__(self, name: str):
        if name in self.__store:
            return self.__store[name]
        raise AttributeError(g_error_msg[6].format(name=name))

    def get_class_by_name(self, name: str, *args) -> object:
        """
        Gets the Class definition by name.

        Raises ValueError if name is not in registry.
        Unless a third argument has been provided, in which case, this will be returned as default value.
        """
        if name in self.__store:
            return self.__store[name]
        if len(args) > 0:
            return args[0]
        raise ValueError(g_error_msg[3].format(name=name))

    def get_name_by_class(self, cls: object, *args) -> str:
        """
        Returns the class registred Name in store.

        Raises ValueError if no class match has been found.
        Unless a third argument has been provided, in which case, this will be
        returned as default value.
        """
        key: str
        for key in self.__store:
            if self.__store[key] == cls:
                return key
        if len(args) > 0:
            return args[0]
        raise ValueError(g_error_msg.format(cls=cls))


# Creates the main instance of a Factory.
Factory = _Factory()

Logger.info("Factory: Module load completed.")
if __name__ == '__main__':
    raise RuntimeError("Error, this file is not meant to be run as __main__.")
