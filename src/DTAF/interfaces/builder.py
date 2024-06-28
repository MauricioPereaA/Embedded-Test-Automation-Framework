# -*- coding: utf-8 -*-
"""
Builder
========

The builder module will store all needed classes and methods to allow DTAF to
build virtual representations of each device based on a `Model` file, this file
will be designed using the YAML structure to easen our device definition and
allow our abstrac classes and bases to automatically build a representation for
you to test.

please, see the documentation of each interface and the how to to learn more
about the viable configurations you may need to set in order for the VDR to
work.

Each interface, device will have their own set of configurations you may need or
want to change to accomodate the VDR into your test bench.
"""
# ---- importations section ----
import pathlib
import weakref
import yaml
import gc
import traceback

#   imports the configuration manager instance.
from DTAF.config import Config
import DTAF.factory

#TODO: remove this block once our own logger has been added.
# temporal Logger
# import logging

# Logger = logging.getLogger("Builder")
from DTAF.logger import SystemLogger as Logger
# </END>

g_warning_msg: tuple[str] = (
    "Builder: Dead reference found in memory. removing UID: {uid} from memory.",  # 0
    "Builder: Removing device from internal memory.",  # 1
    "Builder: Removing interface from internal memory.",  # 2
    "Builder: Path is a folder.",  # 3
    "Builder: Data Type not implemented. please consider notifying your supplier for more information about this error. UID:{uid}, type:{type_}.",  # 4
    "Builder: Missing Structure ID in main tree. {uid}.",  # 5
    "Builder: Device Interface section is empty. device_name: {name}.",  # 6
    "Builder: ",  # x
)

g_error_msg: tuple[str] = (
    "Builder: There can only be one instance of the Builder Class.",  # 0
    "Builder: Missing or incorrect type: name = {name}, type = {type_}, value = {value}.",  # 1
    "Builder: Unknown Error happened. \n\tTYPE: {type_}\n\tERROR: {error}\n\tTRACEBACK: {traceback}\n --- </END> ---",  # 2
    "Builder: TYPE ERROR: intance is neither `device` nor `interface` type: uid={uid}, type={type_}.",  # 3
    "Builder: Model file doesn't exists or is unreachable.",  # 4
    "Builder: Model file is a folder.",  # 5
    "Builder: Invalid UID, there's no registry of [{uid}] in the memory tree.\tkeys: {keys}.",  # 6
    "Builder: Invalid Memory Tree entry: uid={uid}, Entry is missing attributes. {missing_attrs}.",  # 7
    "Builder: Orphan registry found in main memory Tree, entry {uid} was not found in {memory_section}.",  # 8
    "Builder: Model Error: models can only have one root. found: {roots}.",  # 9
    "Builder: Attribute Error, Invalid Attribute name: Name: {name}, Value: {value}",  # 10
    "Builder: ",  # x
)
"""
List of all error messages of this module.
"""

g_required_keys: dict = {
    "Config": {
        "load_sequence": (int, False),  # Load seuqence of importance.
        "log_level": (int, False)  # Defaiñts to warning if not set.
    },
    "Devices": {
        # Name of the device.
        "Name": (str, True),
        # Description of the device.
        "Description": (str, True),
        # model of the device.
        "Model": (str, True),
        # ID of the device, assigned by the end user.
        "id": (int, True),
        # Structure for the interfaces.
        "Interfaces": {
            # Name of the interface
            "name": (str, True),
            # Description of the interface, if none, default class will be set.
            "description": (str, False),
            # Custom ID of the interface.
            "id": (int, True),
            # # Added by the interface class definition.
            # "Type": str,
            # Must be one of the allowed by the interfaces module. Set by the interface class if not present
            "model": (str, False),
            # Lists where the interface is connected to.
            "connections": (list, False),
            # Determines if the interface is connected to the host pc,
            # or to another device. (True: connected from device to host,
            # False, Interface is connected to another device, the value
            # from connections will be used).
            "hosted": (bool, True),
            # End of line scape characters.
            "eol": (str, False),
            # BaudRate of the connection (Serial interfaces)
            "baudrate": (int, False),
            # Timeout Interface setting.
            "timeout": ((int, None), False),
            # Phisical port/device to connect to.
            "port": (str, False),
            # Channel connection (For CAN)
            "channel": (int, False),
        },
    },
}
"""
Dictionary of namespaces.

This memory structure will tell the class which attributes must be
always required, while other not.

the definition keypar will be the attribute type, or types as the first
parameter, and the second one will be a boolean, that will tell the
method which attributes are required to be present, and which not.
"""


class BuilderClass():
    __max_uid: int = 0
    "Current ID counter of all instances."

    @property
    def max_uid(self) -> int:
        """
        This value represents the current amount of UID's assigned.

        it will be incremented by 1 each time a new item is added.

        .. note::
            Each time we add a new item in memory, we will add 1 to the counter,
            this way, we won't need to call len() each time we need to veryfi the
            instance count.

            Since we will be starting from 0, we will assing this value as UID then
            add +1 to the counter.
        """
        return self.__max_uid

    __interfaces: dict = {}

    @property
    def interfaces(self):
        """
        Stores all interface instances by UID.

        .. note::
            This is where we're storing all interface instances in memory, the
            builder method will return a shallow copy/ proxy object to make
            reference to this element.

            The BuilderClass instance will be the one to manage the internal memory
            of all instances.
        """
        return [key for key in self.__interfaces]

    __devices: dict = {}

    @property
    def devices(self):
        """
        Stores all device Instances by UID.

        .. note::
            This is where we're storing all device (VDR) in memory, the builder
            method will return a shallow copy/ proxy object to make reference to
            this element.

            The BuilderClass instance will be the one to manage the internal memory
            of all instances.
        """
        return [key for key in self.__devices]

    __store: dict = {}
    """
    Store allowcation for the
    """

    __root: object = None

    @property
    def root(self):
        """
        Root VDR object.
        This object will represent the master in in the master/slave behavior.

        Thanks to this we may be able to use the device to communicate with it's
        children using a special method or communication interface.

        .. note::
            Not Implemented for now.
            this allowcation has been done in advance of the support.
        """
        return self.__root

    def set_root(self, object: object):
        """
        Sets the current root object.
        """
        self.__root = object

    _flag_initialized: bool = False
    """
    This fall will let the new builder instance to know if there is already
    one in memory.

    If there is already an instance of the BuilderClass class, then we will
    raise a RuntimeException if we try to create another one.

    This attribute will be False by default.
    """

    def __init__(self) -> None:
        if self._flag_initialized is True:
            raise RuntimeError(g_error_msg[0])
        BuilderClass._flag_initialized = True

    @classmethod
    def get_new_UID(cls) -> int:
        """
        Returns a new Integer based on the internal counter.

        The internal counter then will increase in 1.
        """
        cls.__max_uid += 1
        return cls.__max_uid - 1

    @classmethod
    def register_new_interface(cls,
                               interface_instance: object = None,
                               device_instance_uid: int = None,
                               filename: str | pathlib.Path = "MISSING") -> int:
        """
        Registers the new interface in memory and assigns it a single UID as a
        key in memory.

        .. note::
            You may be able to register a new interface without a device that
            it would be bound to. in this case. a log message will be emmited.
        """
        uid: int = cls.get_new_UID()
        cls.__interfaces[uid] = interface_instance
        cls.__store[uid] = {"type": "interface", "devices": {}, "filename": filename}
        cls.__store[uid]["host_device"] = device_instance_uid
        return uid

    @classmethod
    def register_new_device(cls, device_instance: object = None, filename: str | pathlib.Path = "MISSING") -> int:
        """
        Registers a new instance of the device class (VDR) in memory.

        This method registers a new instance of a device and returns their ID,
        it will either return None or raise an exception in the case the task
        failed.
        """
        #TODO: REPLACE CHECK WITH DEVICE CLASS TYPE.
        if device_instance is None:
            raise ValueError(g_error_msg[1].format(type_=type(device_instance),
                                                   name='device_instance',
                                                   value=device_instance))
        uid: int = cls.get_new_UID()
        cls.__devices[uid] = device_instance
        cls.__store[uid] = {"type": "device", "interfaces": {}, "filename": filename}
        return uid

    def validate_string(self, string: str):
        """
        Validates an input string.

        This method will also manage if there is any issue with the model.

        Verifies that the string is indeed a YAML structure between other
        checkups needed.
        """
        string = str(string).strip()
        return string

    def load_string(self, model: str = '', filename: str | pathlib.Path = "Global") -> dict:
        """
        Parses the model into the constructor
        Registers the model into memory Assigns a UID.

        Returns a weakref.proxy object with it's cleaner assigned.
        """
        interface_uid: int
        device_uid: int
        data: dict = {}
        try:
            data = yaml.load(model, Loader=yaml.SafeLoader)
        except Exception as error:
            #TODO: change to logger message.
            Logger.info(g_error_msg[2].format(type_=type(error), error=error, traceback=traceback.format_exc()))
            raise error

        # raise NotImplementedError("This method is still incomplete. please wait until the interface's "
        #                           "modules are completed to continue this section.")
        if len(data.keys()) > 1:
            raise RuntimeError(g_error_msg[9].format(roots=list(data.keys())))
        # Takes the first root
        for device_name in data:
            device = data[device_name]
            device_cls = DTAF.factory.Factory.get_class_by_name(device_name)

            # Creates the class instance and then registers it.
            kwargs = {key: device[key] for key in list(device.keys()) if key != "interfaces"}
            Logger.warning(f"kwargs = {kwargs}")
            device_instance = device_cls(**kwargs)
            device_uid = self.register_new_device(device_instance, filename)

            # sets class attributes.
            # setattr(device_instance, "name", device.get("name", "Null"))
            # setattr(device_instance, "description", device.get("description", "Null"))
            # setattr(device_instance, "model", device.get("model", "Null"))
            # setattr(device_instance, "id", device.get("id", "Null"))
            device_instance.set_uid(device_uid)

            # verify the model has an "interfaces" section.
            if not device["interfaces"]:
                Logger.warning(g_warning_msg[6].format(name=device_name))
                continue

            # loops over all interfaces defined in the model.
            for interface_class_name in device["interfaces"]:
                # assigns an alias for the model section.
                interface_model = device["interfaces"][interface_class_name]
                #interface_model["duid"] = device_uid

                # requests the class type from factory.
                interface_cls = DTAF.factory.Factory.get_class_by_name(interface_class_name)

                # Creates New Interface instance in memory. parses down all attributes from the model.
                Interface = interface_cls(**interface_model)

                # Registers the new interface
                interface_uid = self.register_new_interface(Interface, device_uid, filename)
                Interface.set_duid(device_uid)
                Interface.set_uid(interface_uid)

                # adds the interface to the device.
                device_instance.add_interface(Interface.name, self.get_reference_by_UID(interface_uid))

        return self.get_reference_by_UID(device_uid)

    def load_file(self, filename: str | pathlib.Path) -> weakref.proxy:
        """
        File wrapper for the self.load_string method.

        Returns a weakref.proxy object as it keeps the original instance in
        internal memory.

        This wrapper will allow the user to load files directly using both,
        strings and pathlib.Path like objects.

        The wrapper will manage internal logic to easen the programming load on
        the client side.

        same as load_string, it will register all information on the object, the
        only change will be that the metadata will mark the object loaded with
        this method and the filename may be a pathlib.path object.
        """
        model_string: str = ""
        filename = pathlib.Path(filename)
        if filename.exists() is False:
            raise ValueError(g_error_msg[4])
        elif filename.is_dir() is True:
            raise ValueError(g_error_msg[5])
        elif filename.is_absolute() is False:
            #TODO: change this to a log message.
            Logger.warning(g_warning_msg[3])
        with open(filename, "r") as file_:
            model_string = file_.read()
        return self.load_string(model=model_string, filename=str(filename))

    def call_garbage_collector(self):
        """
        Cleanup method to request the recollection of the garbage collector
        module.
        """
        #TODO: improve this method to run asynchronously.
        gc.enable()
        gc.collect()
        pass

    @classmethod
    def verify_registry(cls):
        """
        Verifies that the storage values are set correctly, and no children are left without a parent.

        This method will look up all memories storage and clean after an object has been discarded.
        It will return True when the scan has been successful, False if there was an error.

        .. warning::
            This method will look the whole tree table and try to find any
            missing or broken object reference in memory, if the reference is
            found dead, the method will remove it from the tree.
        """
        doc: str = ''
        type_: str = ''
        keys = cls.__store[:]
        for key in keys:
            try:
                type_ = cls.__store[key]["type"]
                if type_ == 'device':
                    data = cls.__devices[key]
                elif type_ == 'interface':
                    data = cls.__interfaces[key]
                else:
                    raise ValueError(g_error_msg[3].format(uid=key, type_=type_))
                if data:
                    # we check contents of the object to verify that the object is still alive
                    doc = data.__doc__
                    continue
            except ReferenceError as error:
                #TODO: add here log message
                Logger.warning(g_warning_msg[0].format(uid=key))
                del cls.__store[key]
                # removes reference object from list.
                if key in cls.__devices:
                    Logger.warning(g_warning_msg[1])
                    del cls.__devices[key]

                if key in cls.__interfaces:
                    Logger.warning(g_warning_msg[2])
                    del cls.__interfaces[key]

            except Exception as error:
                #TODO: Adde error log here.
                Logger.error(g_error_msg[2].format(type_=type(error), error=error, traceback=traceback.format_exc()))
                pass

    def get_reference_by_UID(self, uid: int = None) -> weakref.proxy:
        """
        Returns a Proxy that will clean itself after collection from GC.

        It will look into both, device and interface objects
        first check: self.__max_UID<:arg:UID
        """
        # checks the entry is in the main memory tree.
        if uid not in self.__store:
            raise ValueError(g_error_msg[6].format(uid=uid, keys=list(self.__store.keys())))
        type_ = self.__store[uid].get("type", None)
        # checks the model has the type attribute in the entry.
        if type_ is None:
            raise RuntimeError(g_error_msg[7].format(uid=uid, missing_attrs="type"))
        # checks if the entry belongs to a device.
        elif type_ == 'device':
            if uid not in self.__devices:
                raise RuntimeError(g_error_msg[8].format(uid=uid, memory_section="__devices"))
            return weakref.proxy(self.__devices[uid], lambda *x: self.remove_device_by_uid)
        # checks if the entry belongs to an interface.
        elif type_ == 'interface':
            if uid not in self.__interfaces:
                raise RuntimeError(g_error_msg[8].format(uid=uid, memory_section="__interfaces"))
            return weakref.proxy(self.__interfaces[uid], lambda *x: self.remove_device_by_uid)
        else:
            raise NotImplementedError(g_warning_msg[4].format(uid=uid, type_=type_) + " entry: " +
                                      str(self.__store[uid]) + "</END>")
        return None

    def get_UID_by_reference(self, proxy_object: weakref.proxy) -> int:
        """
        Returns the object's UID based on the proxy object.

        Ideally we would try to check the objec internal memory (uid).
        """
        uid: int = None
        for uid in self.__devices:
            if self.__devices[uid] == proxy_object:
                return uid
        for uid in self.__interfaces:
            if self.__devices[uid] == proxy_object:
                return uid
        return uid

    def remove_device_by_UID(self, uid: int) -> bool:
        """
        Removes a Device from memory.

        Removes all interface connections from the device's memory links and builders instance.
        """
        device: object = None
        interfaces: list[int] = []
        pass
        if uid not in self.__devices:
            raise ValueError(g_error_msg[6].format(uid=uid, keys=self.devices) + " type: Interface")
        device = self.get_reference_byeteng_UID(uid)
        interfaces = device.get_interface_list()[:]
        del self.__devices[uid]
        if uid in self.__store:
            del self.__store[uid]
        for interface_id in interfaces:
            self.remove_interface_by_UID(interface_id)
        return True

    def remove_interface_by_UID(self, uid: int) -> bool:
        """
        Removes an interface from memory by their UID

        It will discard any object from the internal structure and their links on
        the main db.
        """
        if uid not in self.__interfaces:
            raise ValueError(g_error_msg[6].format(uid=uid, keys=self.interfaces) + " type: Interface")
        del self.__interfaces[uid]
        if uid in self.__store:
            del self.__store[uid]
        else:
            Logger.warning(g_warning_msg[5].format(uid=uid) + " type: Interface")
        return True

    def remove_interface_by_proxy(self, proxy_object: weakref.proxy) -> bool:
        """
        Removes an interface from memory by their reference proxy.

        It will discard any object from the internal structure and their links
        on the main db.
        """
        uid: int = self.get_UID_by_reference(proxy_object=proxy_object)
        return self.remove_interface_by_UID(uid)

    def remove_device_by_proxy(self, proxy_object: weakref.proxy) -> bool:
        """
        Removes a Device from memory.

        Removes all interface connections from the device's memory links and
        builders instance.
        """
        uid: int = self.get_UID_by_reference(proxy_object=proxy_object)
        return self.remove_device_by_UID(uid)


Builder = BuilderClass()

__all__ = ("Builder", )
