# -*- coding: utf-8 -*-
import smbus
import time
from DTAF.interfaces.interfaces import InterfaceBase


class ConnectionError(Exception):
    """Exception raised for errors in the I2CConnection class."""


class I2CInterface(InterfaceBase):
    """
    A class for establishing an I2C connection with a device.

    Args:
        bus_number: The number of the I2C bus to use.
        device_address: The address of the I2C device to connect to.

    Raises:
        ConnectionError: If the I2C device is not found on the specified bus.

    """

    def __init__(
            self,
            # bus_number: int, device_address: int
            **kwargs):
        """
        Constructor for I2CConnection class.

        Args:
            bus_number: The number of the I2C bus to use.
            device_address: The address of the I2C device to connect to.

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        # sets the deffault value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["bus_number"] = kwargs.get("bus_number", "COM1")
        kwargs["device_address"] = kwargs.get("baudrate", 9600)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        if not isinstance(kwargs['bus_number'], int) or kwargs['bus_number'] < 0:
            raise ValueError(f"Bus number must be a non-negative integer, but got {kwargs['bus_number']} instead.")
        if not isinstance(kwargs['device_address'],
                          int) or kwargs['device_address'] < 0 or kwargs['device_address'] > 0x7F:
            raise ValueError(
                f"Device address must be an integer between 0 and 127, but got {kwargs['device_address']} instead.")
        self.bus_number = kwargs['bus_number']
        self.device_address = kwargs['device_address']
        self.bus = None

    def connect_impl(self, retries: int = 3, delay: float = 0.1) -> None:
        """
        Connect to the I2C device.

        Args:
            retries: The number of times to retry the connection.
            delay: The delay between retries.

        Raises:
            ConnectionError: If the I2C device is not found after the specified number of retries.

        Returns:
            None
        """
        attempts = 0
        while attempts < retries:
            try:
                self.bus = smbus.SMBus(self.bus_number)
                self.bus.write_quick(self.device_address)
                return
            except OSError:
                attempts += 1
                time.sleep(delay)
                raise ConnectionError(f"I2C device not found at address {self.device_address} on bus {self.bus_number}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from the I2C device.

        Returns:
            None
        """
        if self.bus is not None:
            self.bus.close()
            self.bus = None

    def write_impl(self, register_address: int, data: bytes, retries: int = 3, delay: float = 0.1) -> None:
        """
        Write data to a specific register on the I2C device.

        Args:
            register_address: The address of the register to write to.
            data: The data to write to the register.
            retries: The number of times to retry the write operation.
            delay: The delay between retries.

        Raises:
            ConnectionError: If the write operation fails after the specified number of retries.

        Returns:
            None
        """
        attempts = 0
        while attempts < retries:
            try:
                self.bus.write_i2c_block_data(self.device_address, register_address, list(data))
                return
            except OSError:
                attempts += 1
                time.sleep(delay)
                raise ConnectionError(
                    f"Error writing data to register {register_address} on I2C device {self.device_address}")

    def read_impl(self, register_address: int, length: int, retries: int = 3, delay: float = 0.1) -> bytes:
        """
        Read data from a specific register on the I2C device.

        Args:
            register_address: The address of the register to read from.
            length: The number of bytes to read.
            retries: The number of times to retry the read operation.
            delay: The delay between retries.

        Raises:
            ConnectionError: If the read operation fails after the specified number of retries.

        Returns:
            The data read from the register.
        """
        attempts = 0
        while attempts < retries:
            try:
                self.bus.write_byte(self.device_address, register_address)
                time.sleep(delay)
                data = self.bus.read_i2c_block_data(self.device_address, register_address, length)
                return bytes(data)
            except OSError:
                attempts += 1
                time.sleep(delay)
                raise ConnectionError(
                    f"Error reading data from register {register_address} on I2C device {self.device_address}")
