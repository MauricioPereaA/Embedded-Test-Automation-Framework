# -*- coding: utf-8 -*-
from pyftdi.gpio import GpioController, GpioException
from DTAF.interfaces.interfaces import InterfaceBase
from DTAF.interfaces.gpio_pin import Pin

class GPIOException(Exception):
    """Exception class for Bluetooth communication errors"""
    pass

class FT232RGPIOInterface(InterfaceBase):
    """
    Class representing the FT232R GPIO interface for Windows.
    The FT232R GPIO is a USB to serial converter that provides access to GPIO pins.

    :param pins: A dictionary where keys represent pin numbers and values represent
    pin objects. The FT232R supports 12 GPIO pins (0-11).
    """
    def __init__(self, **kwargs):
        """
        Constructor for FT232RGPIOInterface class.

        Args:
            url: URL for the FT232R device. REQUIRED

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        kwargs["url"] = kwargs.get("url", 'ftdi://ftdi:232h/1')

        super().__init__(**kwargs)
        self.gpio = GpioController()
        self.pins = {}

    def connect_impl(self):
        """
        Connects to the FT232R GPIO interface.
        """
        try:
            self.gpio.open_from_url(self.url)
        except GPIOException as e:
            print(f"Failed to connect: {e}")

    def disconnect_impl(self):
        """
        Disconnects from the FT232R GPIO interface.
        """
        self.gpio.close()

    def create_pin(self, pin_number, direction, initial=0):
        """
        Creates a new GPIO pin.
        :param pin_number: The number of the GPIO pin to create.
        :param direction: The direction of the GPIO pin ("input" or "output").
        :param initial: The initial state of the GPIO pin (0 for low, 1 for high).
        """
        if pin_number in self.pins:
            raise GPIOException(f"Pin {pin_number} is already in use.")
        self.pins[pin_number] = Pin(self, pin_number, direction, initial)

    def remove_pin(self, pin_number):
        """
        Removes a GPIO pin.
        :param pin_number: The number of the GPIO pin to remove.
        """
        if pin_number not in self.pins:
            raise GPIOException(f"Pin {pin_number} is not in use.")
        self.pins[pin_number].cleanup()
        del self.pins[pin_number]
