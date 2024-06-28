# -*- coding: utf-8 -*-
import weakref
import copy
import typing

from DTAF.interfaces.interfaces import InterfaceBase

#TODO: remove this section and replace with internal logger.
import logging

from DTAF.logger import DeviceLogger as Logger, SystemLogger
# Logger = logging.getLogger("DeviceLogger")

# </END>

g_error_msg: tuple[str] = (
    "Name already in use. Name: `{name}`.",  # 0
    "Name not found in registry. Name: `{name}`.",  # 1
    "Dead object Reference. Name: `{name}`.",  # 2
    "Device has already an UID assigned. current: {uid}, new: {new}",  # 3
    "Wrong Type: attribute [{name}] has to be type [{type_}], found [{type__}], Value: {value}",  # 4
    "DeviceBase: ",  # x
)
g_debug_msg: tuple[str] = (
    "Requested Attribute name: {name}",  # 0
    "Added new interface [{uid}] in memory: name={interface_name}, reference={reference}.",  # 1
    "Removed Interface from memory: name={interface_name}, reference={reference}.",  # 2
    "Requested interface list.",  # 3
    "DeviceBase: ",  # x
)

g_warning_msg: tuple[str] = (
    "Attribute [{name}] not found in __store, assigning memory space for value: {value}",  # 0
    "DeviceBase: ",  # x
)

g_store_pattern: dict = {
    "interfaces": {},
    "name": "Null",
    "uid": "Null",
    "model": "Null",
}


class DeviceBase():
    """
    Base class for all Devices.

    This class defines the base behavior of each device in memory.

    Features:
        Interface memory allocation and management.
    """
    name: str = 'Null'
    """
    Assigned Name of the device.

    Assigned by the client.
    """

    id: int = 999
    """
    User assigned ID.

    This ID will be used as meta data, to be compatible with external ID
    assignation.

    .. warning::
        Keep in mind that this `ID` attribute is not the same as the :attr int `UID`:

        This ID is for you (the third party user) to assign a custom ID to be
        compatible with your framework.
    """

    __uid: int = None

    @property
    def uid(self):
        """
        UID of the device instance.

        set by the builder.
        """
        return self.__uid

    def set_uid(self, uid: int):
        if isinstance(uid, int) is False:
            raise ValueError(g_error_msg[4].format(name='uid', type_="int", type__=(type(uid)), value=uid))
        if self.__uid is None:
            self.__uid = uid
            self.logger = logging.LoggerAdapter(Logger, {
                "uid": self.uid,
                "device_class": str(self.__class__).split(".")[-1][:-2]
            })
        else:
            raise ValueError(g_error_msg[3].format(uid=self.__uid, new=uid))

    __store: dict = {}

    logger: logging.Logger = None

    @property
    def store(self):
        """
        internal storage of the class.

        This property will only return a shallow copy.
        """
        return copy.deepcopy(self.__store)

    def __init__(self, **kwargs) -> None:
        # stores values in
        if 'duid' in kwargs:
            raise ValueError("Invalid attribute name \"duid\". A device can't have a assigned another device.")
        if "uid" in kwargs:
            self.set_uid(kwargs["uid"])
        self.logger = SystemLogger
        # self.logger = logging.LoggerAdapter(Logger, {
        #     "uid": self.uid,
        #     "device_class": str(self.__class__).split(".")[-1][:-2]
        # })
        # init the interface store.
        self.__store["interfaces"] = {}
        # Assigns default Value for kwargs
        kwargs["name"] = kwargs.get("name", "UNKNOWN")
        kwargs["id"] = kwargs.get("id", 9999)
        kwargs["model"] = kwargs.get("model", "Generic")
        kwargs["description"] = kwargs.get("description", "UNKNOWN")
        for key in kwargs:
            if key in ['interfaces', "duid", "uid"]:
                continue
            elif key in dir(self):
                setattr(self, key, kwargs[key])
            self.__store[key] = kwargs[key]

    def add_interface(self, name: str, interface_reference: weakref.ref) -> bool:
        """
        Adds an interface to storage.

        Returns True if task is done succesfully.
        """
        self.logger.debug(g_debug_msg[1].format(interface_name=name,
                                                reference=interface_reference,
                                                uid=interface_reference.uid))
        if name in self.__store["interfaces"]:
            raise NameError(g_error_msg[0].format(name=name))
        self.__store["interfaces"][name] = interface_reference
        return True

    def remove_interface(self, name: str, interface_reference: weakref.ref = None) -> bool:
        """
        Removes an interface from storage.

        Returns True if task is Done Successfully.
        """
        self.logger.debug(g_debug_msg[2].format(interface_name=name, reference=interface_reference))
        if name in self.__store["interfaces"]:
            del self.__store["interfaces"][name]
            return True
        return False

    def get_interfaces(self) -> list[str]:
        """
        Returns a list of interface names.

        returns: list[str]
        """
        self.logger.debug(g_debug_msg[3])
        return list(self.__store["interfaces"].keys())

    @property
    def interfaces(self) -> list[str]:
        return self.get_interfaces()

    def __getattr__(self, name: str):
        self.logger.debug(g_debug_msg[0].format(name=name))
        # Returns the interface from __store[interfaces].
        if name in self.__store["interfaces"]:
            return self.__store["interfaces"][name]
        # Returns the attribute from __store.
        elif name in self.__store:
            return self.__store[name]
        # The name is really nowhere in the instance.
        raise AttributeError(g_error_msg[1].format(name=name))

    def __setattr__(self, attr: str, value: typing.Any):
        # if attribute is not in the list of registered attributes
        if attr not in dir(self):
            # We store the new attribute inside
            if attr not in self.__store:
                # print(f"missing attr:{attr}, value: 'value'")
                self.logger.warning(g_warning_msg[0].format(name=attr, value=value))
            self.__store[attr] = value
            return
        super().__setattr__(attr, value)

    def clean_store(self, *dt):
        self.__store = copy.deepcopy(g_store_pattern)
