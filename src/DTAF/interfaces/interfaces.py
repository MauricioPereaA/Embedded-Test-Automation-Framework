# -*- coding: utf-8 -*-
import time
import typing
import copy
import logging
import traceback

from DTAF.logger import InterfaceLogger as Logger, SystemLogger


class InterfaceBase:
    """
    Base class for communication interfaces with a device.

    Subclasses of this class should implement the methods `connect_impl`, `disconnect_impl`,
    `read_impl`, and `write_impl` to define the interface for communication with a device.

    Attributes:
        connection: The connection object for the interface, initialized to None.
        logfile: The filename of the log file for the interface, initialized to None.
    """

    __store: dict = {}
    """
    Memory Storage area.

    This is where we store any non standard attributes by name and value.
    """

    connection = None
    """
    Current Device connection.

    This represents the current I/O file-descriptor, object or FIFO.
    """

    logger: logging.Logger = None
    """
    Current logger pointer.

    This is a LoggerAdapter object based from the InterfaceLogger object that
    enables the custom format issued in the configuration module,
    using the setting from the configuration file.
    """

    uid: int = None
    """
    Interface unique ID.

    This is the unique id that allows the memory manager to find the object
    instance in the internal memory of the builder.

    Both interface and device IDs can't be the same number. they're from the
    same scale.
    """

    duid: int = None
    """
    Device Unique ID.

    This is the device the interface is bound to.
    Both interface and device IDs can't be the same number. they're from the same scale.
    """

    __uid: int = None
    """
    Internal storage of the UID.
    """

    __duid: int = None
    """
    Internal storage of the DUID.
    """

    def __load_logger(self):
        self.logger = logging.LoggerAdapter(Logger, {
            "uid": str(self.uid),
            "duid": str(self.duid),
            "interface_class": self.__class__
        })

    def __getattr__(self, attr: str) -> typing.Any:
        if attr in self.__store:
            return self.__store[attr]
        raise ValueError("InterfaceBase: getattr :: Unable to find attribute `{}`, not found in __store.".format(attr))

    def __setattr__(self, attr: str, value: typing.Any) -> None:
        if attr not in dir(self):
            # TODO: ADD LOG MESSAGE HERE TO INDICATE WE ADDED A NEW ATTRIBUTE
            # if attr not in self.__store:
            #     Logger.warning("Attribute [{name}] not found in __store, assigning memory space for value: {value}".format (name = attr, value = value))
            self.__store[attr] = value
            return
        super().__setattr__(attr, value)

    @property
    def uid(self) -> None:
        """
        Unique ID of the interface.

        This value is assigned by the builder when the interface is initialized.
        """
        return self.__uid

    def set_uid(self, uid: int | str):
        # SystemLogger.debug(f"INTERFACES: Setting Interface UID: {uid}")
        if isinstance(uid, (int, str)) is False:
            raise ValueError("InterfaceBase: uid :: Attribute Error, attribute Wrong Type: attribute "
                             "[{name}] has to be type [{type_}], found [{type__}], Value: {value}".format(
                                 name='uid', type_='int', type__=type(uid), value=uid))
        if isinstance(self.__uid, int) is False:
            self.__uid = uid
        else:
            raise ValueError("InterfaceBase: uid :: Device UID already assigned. current {}, new {}".format(
                self.__uid, uid))

    # sets device UID
    @property
    def duid(self) -> None:
        """
        Unique ID of the interface.

        This value is assigned by the builder when the interface is initialized.
        """
        return self.__uid

    def set_duid(self, duid: int | str):
        """
        sets device UID.
        """
        # SystemLogger.debug(f"INTERFACES: Setting device UID: {duid}, uid: {self.uid}")
        if isinstance(duid, (int, str)) is False:
            raise ValueError("InterfaceBase: duid :: Attribute Error, attribute Wrong Type: attribute "
                             "[{name}] has to be type [{type_}], found [{type__}], Value: {value}".format(
                                 name='uid', type_='int', type__=type(duid), value=duid))
        if isinstance(self.__duid, int) is False:
            self.__duid = duid
        else:
            raise ValueError("InterfaceBase: duid :: Device UID already assigned. current {}, new {}".format(
                self.__duid, duid))

    __interface_names: list[str] = []
    __interface_counter: int = 0

    @staticmethod
    def get_new_interface_name(counter: int) -> str:
        """
        Gets a new default name for interfaces without a name attr in model.
        """
        InterfaceBase.__interface_names.append("Interface_" + str(counter))
        return InterfaceBase.__interface_names[-1]

    @staticmethod
    def remove_interface_name(name: str) -> bool:
        """
        Removes an interface Name from memory.
        """
        if name not in InterfaceBase.__interface_names:
            raise ValueError(
                "InterfaceBase: remove_interface_name :: Invalid Name. The name [{name}] is not registered.".format(
                    name))
        InterfaceBase.__interface_names.remove(name)
        return True

    @staticmethod
    def add_interface_name(name: str) -> bool:
        """
        Adds a new interface name in memory.
        """
        if name in InterfaceBase.__interface_names:
            raise ValueError("InterfaceBase: add_interface_name :: Name already in use: [{name}]".format(name=name))
        InterfaceBase.__interface_names.append(name)
        return True

    @staticmethod
    def rename_interface(old_name: str, new_name: str) -> bool:
        """
        Renames a new interface in memory.
        """
        if old_name in InterfaceBase.__interface_names:
            InterfaceBase.__interface_names.remove(old_name)
            InterfaceBase.__interface_names.append(new_name)
        return True

    @staticmethod
    def get_interface_names(self):
        """
        returns a shallow copy of the list of interface names.
        """
        return copy.copy(InterfaceBase.__interface_names)

    @classmethod
    def add_interface_counter(cls) -> int:
        cls.__interface_counter += 1

    def __init__(self, **kwargs):
        # gets the configuration ids
        self.set_uid(kwargs.get("uid", "UNKNOWN"))
        self.set_duid(kwargs.get("duid", "UNKNOWN"))
        self.__load_logger()

        # sets the general attributes for memory management.
        interface_counter = self.add_interface_counter()
        kwargs["name"] = kwargs.get("name", self.get_new_interface_name(interface_counter))

        self.connection = None
        self.__store = {}

        for attr in kwargs:
            if attr in dir(self) and not attr in ["logfile", "connection", 'uid', 'duid']:
                setattr(self, attr, kwargs[attr])
                continue
            self.__store[attr] = kwargs[attr]

    def connect(self) -> None:
        """
        Connect to the interface.

        This method calls the method `connect_impl` to perform the actual connection.
        If the connection is successful, a log message is recorded.

        Raises:
            Exception: If the connection fails.

        Returns:
            None
        """
        try:
            self.connection = self.connect_impl()
            self.logger.info("InterfaceBase: connect :: Connected to {}".format(self.connection))
        except Exception as e:
            raise Exception("InterfaceBase: connect :: Error connecting to interface: {}".format(str(e)))

    def connect_impl(self) -> object:
        """
        Method to connect to the interface.

        This method must be implemented by subclasses to perform the actual connection.

        Returns:
            A connection object representing the connection to the interface.
        """
        raise NotImplementedError("InterfaceBase: connect_impl :: connect_impl method must be implemented by subclass")

    def disconnect(self) -> None:
        """
        Disconnect from the interface.

        This method calls the method `disconnect_impl` to perform the actual disconnection.
        If the disconnection is successful, a log message is recorded.

        Raises:
            Exception: If the disconnection fails.

        Returns:
            None
        """
        try:
            self.disconnect_impl()
            self.logger.info("InterfaceBase: disconnect :: Disconnected from {}".format(self.connection))
            self.connection = None
        except Exception as error:
            raise Exception(
                "InterfaceBase: disconnect :: Error disconnecting from interface: \nERROR:\t{}\nTYPE:\t{}\nTRACEBACK: {}\n--- <TRACEBACK END> ---"
                .format(error, type(error), traceback.format_exc()))

    def disconnect_impl(self) -> None:
        """
        Method to disconnect from the interface.

        This method must be implemented by subclasses to perform the actual disconnection.

        Args:
            connection: The connection object representing the connection to the interface.

        Returns:
            None
        """
        raise NotImplementedError(
            "InterfaceBase: disconnect_impl :: disconnect_impl method must be implemented by subclass")

    def read(self) -> bytes:
        """
        Read data from the interface.

        This method calls the method `read_impl` to read data from the interface.
        If the read is successful, a log message is recorded.

        Raises:
            Exception: If the read operation fails.

        Returns:
            The data read from the interface as bytes.
        """
        try:
            data = self.read_impl()
            self.logger.debug("InterfaceBase: read :: Read {} bytes from {}, data: {}".format(
                len(data), self.connection, data))
            return data
        except Exception as error:
            self.logger.exception("InterfaceBase: read :: Unable to read from interface.", error)
            raise

    def read_impl(self) -> bytes:
        """
        Method to read data from the interface.

        This method must be implemented by subclasses to read data from the interface.

        Args:
            connection: The connection object representing the connection to the interface.

        Returns:
            The data read from the interface.
        """
        raise NotImplementedError("InterfaceBase: read_impl :: read_impl method must be implemented by subclass")

    def write(self, data: bytes) -> None:
        """
        Write data to the interface.

        This method calls the method `write_impl` to write data to the interface.
        If the write is successful, a log message is recorded.

        Args:
            data: The data to write to the interface.

        Raises:
            Exception: If the write operation fails.

        Returns:
            None
        """
        try:
            self.write_impl(data)
            self.logger.debug("InterfaceBase: write :: Wrote {} bytes to {}, data: {}".format(
                len(data), self.connection, data))
        except Exception as error:
            self.logger.exception("InterfaceBase: write :: Unable to write into interface.", exc_info=error)
            raise

    def log(self, message, level=logging.INFO):
        """
        Compatibility layer between old logging method and new.
        """
        if level == logging.DEBUG:
            self.logger.debug(message)
            return
        elif level == logging.INFO:
            self.logger.info(message)
            return
        elif level == logging.WARNING:
            self.logger.warning(message)
            return
        else:
            pass
        self.logger.info(message)

    def write_impl(self, data: bytes) -> None:
        """
        Method to write data to the interface.

        This method must be implemented by subclasses to write data to the interface.

        Args:
            connection: The connection object representing the connection to the interface.
            data: The data to write to the interface.

        Returns:
            None
        """
        raise NotImplementedError("InterfaceBase: write_impl :: write_impl method must be implemented by subclass.")

    def __enter__(self):
        self.connect()

    def __exit__(self):
        self.disconnect()
