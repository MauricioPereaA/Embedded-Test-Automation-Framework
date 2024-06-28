# -*- coding: utf-8 -*-
import spidev
import time
from DTAF.interfaces.interfaces import InterfaceBase


class SPIInterface(InterfaceBase):
    """Class for SPI connection to a device."""

    def __init__(
            self,
            # bus_number, device_number, mode=0, max_speed_hz=500000
            **kwargs):
        """
        Initializes the SPIConnection object.

        Args:
            bus_number (int): SPI bus number, e.g. 0 for "/dev/spidev0.0".
            device_number (int): Chip select (CS) pin number.
            mode (int): SPI mode (0, 1, 2, or 3).
            max_speed_hz (int): Maximum clock speed (in Hz).
        """
        # sets the deffault value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["bus_number"] = kwargs.get("bus_number", 0)
        kwargs["device_number"] = kwargs.get("device_number", 0)
        kwargs["mode"] = kwargs.get("mode", 0)
        kwargs["max_speed_hz"] = kwargs.get("max_speed_hz", 500000)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        self.bus_number = kwargs['bus_number']
        self.device_number = kwargs['device_number']
        self.mode = kwargs['mode']
        self.max_speed_hz = kwargs['max_speed_hz']
        self.spi = None

    def connect_impl(self, retries=3, delay=0.1):
        """
        Connects to the SPI device.

        Args:
            retries (int): Number of times to retry connection on failure.
            delay (float): Delay between connection attempts (in seconds).

        Raises:
            ConnectionError: If unable to connect to the device after retries.
        """
        for i in range(retries):
            try:
                self.spi = spidev.SpiDev()
                self.spi.open(self.bus_number, self.device_number)
                self.spi.max_speed_hz = self.max_speed_hz
                self.spi.mode = self.mode
                return
            except (OSError, IOError) as e:
                self.disconnect()
                time.sleep(delay)
                raise ConnectionError(
                    f"Unable to connect to device on bus {self.bus_number} and CS {self.device_number}. Error: {e}")

    def disconnect_impl(self):
        """
        Disconnects from the SPI device.
        """
        if self.spi:
            try:
                self.spi.close()
            except (OSError, IOError):
                pass
            self.spi = None

    def write_impl(self, data, retries=3, delay=0.1):
        """
        Writes data to the SPI device.

        Args:
            data (bytes): Data to write.
            retries (int): Number of times to retry on failure.
            delay (float): Delay between retries (in seconds).

        Raises:
            ConnectionError: If unable to write to the device after retries.
        """
        for i in range(retries):
            try:
                self.spi.writebytes(list(data))
                return
            except (OSError, IOError) as e:
                self.disconnect()
                time.sleep(delay)
                raise ConnectionError(
                    f"Unable to write data to device on bus {self.bus_number} and CS {self.device_number}. Error: {e}")

    def read_impl(self, length, retries=3, delay=0.1):
        """
        Reads data from the SPI device.

        Args:
            length (int): Number of bytes to read.
            retries (int): Number of times to retry on failure.
            delay (float): Delay between retries (in seconds).

        Raises:
            ConnectionError: If unable to read from the device after retries.

        Returns:
            bytes: Data read from the device.
        """
        for i in range(retries):
            try:
                data = self.spi.readbytes(length)
                return bytes(data)
            except (OSError, IOError) as e:
                self.disconnect()
                time.sleep(delay)
                raise ConnectionError(
                    f"Unable to read data from device on bus {self.bus_number} and CS {self.device_number}. Error: {e}")

    def transfer(self, data, retries=3, delay=0.1):
        """
        Performs a full-duplex SPI transaction with the device.

        Args:
            data (bytes): Data to write.
            retries (int): Number of times to retry on failure.
            delay (float): Delay between retries (in seconds).

        Raises:
            ConnectionError: If unable to perform the transaction after retries.

        Returns:
            bytes: Data returned by the device.
        """
        for i in range(retries):
            try:
                response = self.spi.xfer2(list(data))
                return bytes(response)
            except (OSError, IOError) as e:
                self.disconnect()
                time.sleep(delay)
                raise ConnectionError(f"Unable to perform SPI transaction with device on bus\
                    {self.bus_number} and CS {self.device_number}. Error: {e}")
