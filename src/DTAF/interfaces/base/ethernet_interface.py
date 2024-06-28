# -*- coding: utf-8 -*-
import socket
import re

from DTAF.interfaces.interfaces import InterfaceBase


class ConnectionError(Exception):
    """Exception class for communication errors."""
    pass


class EthernetInterface(InterfaceBase):
    """Class to establish an ethernet connection with a device via COM333 interface."""
    __port: int = 50000
    __ip_address: str = ''
    __socket: socket.socket = None
    __is_connected: bool = False
    __is_configured: bool = False

    def __init__(self, **kwargs):
        # ip_address: str, port: int, type_of_ip: str = "IPv4",
        # type_of_communication: str = "TCP", fileno: int = None
        """
        Constructor for EthernetConnection class.

        Args:
            ethernet_dict: Dictionary with ethernet configuration

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """

        # sets the deffault value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["ip_address"] = kwargs.get("ip_address", "127.0.0.1")
        kwargs["port"] = kwargs.get("port", 8000)
        kwargs["type_of_ip"] = kwargs.get("type_of_ip", 'IPv4')
        kwargs["type_of_communication"] = kwargs.get("type_of_communication", 'TCP')
        kwargs["fileno"] = kwargs.get("fileno", None)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        self.__ip_address = kwargs['ip_address']
        self.__port = kwargs['port']

        socket_family = socket.AF_INET6 if kwargs['type_of_ip'] == "IPv6" else socket.AF_INET

        if not isinstance(self.__ip_address, str):
            raise ValueError(f"IP Address must be a string, but got {type(self.__ip_address)} instead.")
        if not bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", self.__ip_address)):
            raise ValueError("Invalid IP Address.")
        if not isinstance(self.__port, int):
            raise ValueError(f"Port must be an integer, but got {type(self.__port)} instead.")
        if self.__port < 1024 or self.__port > 65535:
            raise ValueError(f"Port must be an integer between 1024 and 65535, but got {self.__port} instead.")

        if kwargs['type_of_communication'] == "UDP":
            self.__socket = socket.socket(socket_family,
                                          socket.SOCK_DGRAM,
                                          proto=socket.SOL_UDP,
                                          fileno=kwargs['fileno'])
        else:
            self.__socket = socket.socket(socket_family, socket.SOCK_STREAM, fileno=kwargs['fileno'])
        self.__is_configured = True

    def connect_impl(self) -> None:
        """
        Connect to tcp socket.

        Raises:
            ConnectionError: If connection fails.

        Returns:
            None
        """
        if self.__is_connected:
            return
        try:
            self.__socket.connect((self.__ip_address, self.__port))
            self.__is_connected = True
        except socket.error as e:
            self.__socket = None
            raise ConnectionError(
                f"Could not connect to ip address {self.__ip_address} and port {self.__port}: {str(e)}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from tcp socket.

        Raises:
            ConnectionError: If disconnection fails.

        Returns:
            None
        """
        if not self.__is_connected:
            return
        try:
            self.__socket.close()
            self.__is_connected = False
        except socket.error as e:
            self.__socket = None
            raise ConnectionError(
                f"Could not disconnect from ip address {self.__ip_address} and port {self.__port}: {str(e)}")

    def write_impl(self, data: bytes) -> None:
        """
        Write data to the tcp socket.

        Args:
            data: Data to write to the tcp socket.

        Raises:
            ConnectionError: If write operation fails.

        Returns:
            None
        """
        if not self.is_connected:
            raise ConnectionError(f"Cannot write data to ip {self.__ip_address} and port {self.__port}: not connected.")
        try:
            self.__socket.sendall(data)
        except socket.error as e:
            raise ConnectionError(f"Failed to write data to ip {self.__ip_address} and port {self.__port}: {str(e)}")

    def read_impl(self, num_bytes: int) -> bytes:
        """
        Read data from the serial port.

        Args:
            num_bytes: Number of bytes to read from the socket.

        Raises:
            ConnectionError: If read operation fails.

        Returns:
            Data read from the socket.
        """
        if not self.is_connected:
            raise ConnectionError(f"Cannot read data to ip {self.__ip_address} and port {self.__port}: not connected.")
        try:
            return self.__socket.recv(num_bytes)
        except socket.error as e:
            raise ConnectionError(f"Failed to write data to ip {self.__ip_address} and port {self.__port}: {str(e)}")

    @property
    def is_connected(self) -> bool:
        """Property to return if the connection is on or off"""
        return self.__is_connected

    @property
    def ip_address(self) -> str:
        """Property to return the ip address"""
        return self.__ip_address

    @property
    def port(self) -> int:
        """Property to return the port"""
        return self.__port

    @property
    def is_configured(self) -> int:
        """Returns True if ethernet is configured in YAML file"""
        return self.__is_configured
