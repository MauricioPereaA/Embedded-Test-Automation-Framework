# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
from DTAF.interfaces.interfaces import InterfaceBase
from DTAF.interfaces.gpio_pin import Pin

class GPIOException(Exception):
    """Exception class for Bluetooth communication errors"""
    pass


class GPIOInterface(InterfaceBase):
    """
    A class to handle GPIO interface communication with a device.

    This class extends InterfaceBase and implements the methods `connect_impl`, `disconnect_impl`.

    Attributes:
        pins (dict): A dictionary mapping GPIO pin numbers to Pin objects that the interface will use.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pins = {}

    def connect_impl(self):
        """
        Method to connect to the GPIO interface.

        This method sets up the GPIO pins for communication.

        Returns:
            The connection object representing the connection to the GPIO interface.
        """
        GPIO.setmode(GPIO.BCM)  # Set the mode to use GPIO numbers, not pin numbers
        for pin in self.pins.values():
            pin.setup()  # Set the pin as an output pin
        return self.pins

    def disconnect_impl(self):
        """
        Method to disconnect from the GPIO interface.

        This method cleans up all the GPIO pins that were set up for communication.

        Returns:
            None
        """
        for pin in self.pins.values():
            pin.cleanup()
        GPIO.cleanup()

    def create_pin(self, pin_number, direction, initial=GPIO.LOW):
        """
        Creates a new Pin object and adds it to the interface.

        Args:
            pin_number: The GPIO pin number.
            direction: The direction of the pin (GPIO.IN or GPIO.OUT).
            initial: The initial state of the pin (GPIO.HIGH or GPIO.LOW). Defaults to GPIO.LOW.

        Raises:
            GPIOException: If the pin is already in use.
        """
        if pin_number in self.pins:
            raise GPIOException(f"Pin {pin_number} is already in use.")
        self.pins[pin_number] = Pin(self, pin_number, direction, initial)

    def remove_pin(self, pin_number):
        """
        Removes a Pin object from the interface and cleans up the pin.

        Args:
            pin_number: The GPIO pin number.

        Raises:
            GPIOException: If the pin is not in use.
        """
        if pin_number not in self.pins:
            raise GPIOException(f"Pin {pin_number} is not in use.")
        self.pins[pin_number].cleanup()
        del self.pins[pin_number]
