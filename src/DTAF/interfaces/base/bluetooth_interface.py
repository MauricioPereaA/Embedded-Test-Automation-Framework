# -*- coding: utf-8 -*-
import bluetooth
from DTAF.interfaces.interfaces import InterfaceBase


class BluetoothException(Exception):
    """Exception class for Bluetooth communication errors"""
    pass


class BluetoothInterface(InterfaceBase):
    """Class to establish a bluetooth coonection with a device"""

    def __init__(
            self,
            # mac_address: str, port: int = 1, timeout: float = 1
            **kwargs):
        """
        Constructor for Bluetooth class.

        Args:
            mac_address: mac address to connect to. REQUIRED
            port: Port of the device to connect to (default 1). Optional
            timeout: Timeout for read operations in seconds (default 1). OPTIONAL

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        # sets the default value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["mac_address"] = kwargs.get("mac_address", '84:76:37:80:A0:B3')
        kwargs["port"] = kwargs.get("port", 1)
        kwargs["timeout"] = kwargs.get("timeout", 1)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        if not isinstance(kwargs['mac_address'], str):
            raise ValueError(f"MAC address must be a string, but got {type(kwargs['mac_address'])} instead.")
        if not isinstance(kwargs['port'], int) or kwargs['port'] <= 0:
            raise ValueError(f"Port must be a positive integer, but got {kwargs['port']} instead.")
        if not isinstance(kwargs['timeout'], (float, int)) or kwargs['timeout'] <= 0:
            raise ValueError(f"Timeout must be a positive float or integer, but got {kwargs['timeout']} instead.")
        self.mac_address = kwargs['mac_address']
        self.port = kwargs['port']
        self.timeout = kwargs['timeout']
        self.socket = None

    def connect_impl(self) -> None:
        if self.is_connected():
            return
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.mac_address, self.port))
        except bluetooth.BluetoothError as e:
            raise BluetoothException(f"Could not connect to {self.mac_address}: {str(e)}")

    def disconnect_impl(self) -> None:
        if self.is_connected():
            self.socket.close()
            self.socket = None

    def write_impl(self, data: bytes) -> None:
        if not self.is_connected():
            raise BluetoothException(f"Cannot write to {self.mac_address}, not connected.")
        try:
            self.socket.send(data.encode())
        except bluetooth.BluetoothError as e:
            self.disconnect()
            raise BluetoothException(f"Error writing data to {self.mac_address}: {str(e)}")

    def read_impl(self) -> bytes:
        if not self.is_connected():
            raise BluetoothException(f"Cannot read from {self.mac_address}, not connected")
        try:
            return self.socket.recv(1024).strip()
        except bluetooth.BluetoothError as e:
            self.disconnect()
            raise BluetoothException(f"Error readingv data from {self.mac_address}: {e}") from e

    def is_connected(self) -> bool:
        return self.socket is not None
