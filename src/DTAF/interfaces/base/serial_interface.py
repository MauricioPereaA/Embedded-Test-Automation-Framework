# -*- coding: utf-8 -*-
import serial
from DTAF.interfaces.interfaces import InterfaceBase


class SerialException(Exception):
    """Exception class for serial communication errors."""
    pass


class SerialInterface(InterfaceBase):
    """Class to establish a serial connection
        with a device via COM interface.
    """

    def __init__(
            self,
            # port: str = "COM1", baudrate: int = 9600, timeout: float = 1,
            **kwargs):
        """
        Constructor for SerialConnection class.

        Args:
            port: Serial port to connect to. REQUIRED
            baudrate: Baud rate of the serial connection (default 9600). OPTIONAL
            timeout: Timeout for read operations in seconds (default 1). OPTIONAL

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        # sets the deffault value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["port"] = kwargs.get("port", "COM1")
        kwargs["baudrate"] = kwargs.get("baudrate", 9600)
        kwargs["timeout"] = kwargs.get("timeout", 1)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        # Serial Interface Specific initialization.
        if not isinstance(kwargs["port"], str):
            raise ValueError(f"Port name must be a string, but got {type(kwargs['port'])} instead.")
        if not isinstance(kwargs["baudrate"], int) or kwargs["baudrate"] <= 0:
            raise ValueError(f"Baudrate must be a positive integer, but got {kwargs['baudrate']} instead.")
        if not isinstance(kwargs["timeout"], (float, int)) or kwargs["timeout"] <= 0:
            raise ValueError(f"Timeout must be a positive float or integer, but got {kwargs['timeout']} instead.")
        self.port = kwargs["port"]
        self.baudrate = kwargs["baudrate"]
        self.timeout = kwargs["timeout"]
        self.serial = None

    def connect_impl(self) -> None:
        """
        Connect to the serial port.

        Raises:
            SerialException: If connection fails.

        Returns:
            None
        """
        if self.is_connected():
            return
        try:
            self.serial = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.timeout)
        except serial.SerialException as e:
            self.serial = None
            raise SerialException(f"Could not connect to {self.port}: {str(e)}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from the serial port.

        Returns:
            None
        """
        try:
            if self.is_connected():
                self.serial.close()
                self.serial = None
            else:
                raise SerialException(f"Error disconecting from {self.port}")
        except Exception as e:
            raise SerialException(f"Error disconecting from {self.port}: {str(e)}")

    def write_impl(self, data: bytes) -> None:
        """
        Write data to the serial port.

        Args:
            data: Data to write to the serial port.

        Raises:
            SerialException: If write operation fails.

        Returns:
            None
        """
        if not self.is_connected():
            raise SerialException(f"Cannot write to {self.port}, not connected.")
        try:
            self.serial.write(data.encode())
        except serial.SerialException as e:
            self.disconnect()
            raise SerialException(f"Error writing data to {self.port}: {str(e)}")

    def read(self, num_bytes: int) -> bytes:
        """
        Read data from the serial port.

        Args:
            num_bytes: Number of bytes read from the port

        Raises:
            SerialException: If read operation fails.

        Returns:
            Data read from the serial port.
        """
        if not self.is_connected():
            raise SerialException(f"Cannot read from {self.port}, not connected.")
        try:
            return self.serial.read(size=num_bytes)
        except serial.SerialException as e:
            self.disconnect()
            raise SerialException(f"Error reading data from {self.port}: {e}") from e

    def read_line(self) -> bytes:
        """
        Read line data from the serial port.

        Raises:
            SerialException: If read operation fails.

        Returns:
            Data read from the serial port.
        """
        if not self.is_connected():
            raise SerialException(f"Cannot read from {self.port}, not connected.")
        try:
            return self.serial.readline().strip()
        except serial.SerialException as e:
            self.disconnect()
            raise SerialException(f"Error reading data from {self.port}: {e}") from e

    def read_until(self, num_bytes: int, match= b'/n') -> bytes:
        """
        Read data from the serial server until macth byte is found.

        Raises:
            SeralException: If read operation fails.

        Returns:
            Data read from the Serial server.
        """
        try:
            return self.serial.read_until(expected=match, size=num_bytes)
        except EOFError as error:
            raise

    def is_connected(self) -> bool:
        """
        Returns whether or not the serial connection is currently open.

        Returns:
            bool: True if the serial connection is open, False otherwise.
        """
        return self.serial is not None and self.serial.is_open
