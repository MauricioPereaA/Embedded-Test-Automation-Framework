# -*- coding: utf-8 -*-

class Pin:
    """Class to represent and interact with a single GPIO pin"""

    def __init__(self, interface, pin_number, direction, initial=GPIO.LOW if isinstance(interface, GPIOInterface) else 0):
        """
        Constructor for Pin class.

        Args:
            interface: The GPIO interface to which this pin belongs.
            pin_number: GPIO pin number to interact with.
            direction: Direction of the pin (GPIO.IN or GPIO.OUT for Raspberry Pi, "input" or "output" for FT232R)
            initial: Initial value for the pin (GPIO.HIGH or GPIO.LOW for Raspberry Pi, 0 or 1 for FT232R)

        Returns:
            None
        """
        self.interface = interface
        self.pin_number = pin_number
        self.direction = direction
        self.initial = initial
        self.pwm = None

        if isinstance(self.interface, GPIOInterface):
            GPIO.setup(self.pin_number, self.direction, initial=self.initial)
        elif isinstance(self.interface, FT232RGPIOInterface):
            if self.direction == "output":
                self.interface.gpio.set_direction(self.pin_number, 0)
            elif self.direction == "input":
                self.interface.gpio.set_direction(self.pin_number, 1)
            else:
                raise GPIOException(f"Invalid direction {self.direction} for pin {self.pin_number}.")

    def set_high(self):
        """
        Sets the pin to high value
        """
        if isinstance(self.interface, GPIOInterface):
            GPIO.output(self.pin_number, GPIO.HIGH)
        elif isinstance(self.interface, FT232RGPIOInterface):
            if self.direction != "output":
                raise GPIOException(f"Pin {self.pin_number} is not an output pin.")
            self.interface.gpio.write(self.pin_number, 1)

    def set_low(self):
        """
        Sets the pin to low value
        """
        if isinstance(self.interface, GPIOInterface):
            GPIO.output(self.pin_number, GPIO.LOW)
        elif isinstance(self.interface, FT232RGPIOInterface):
            if self.direction != "output":
                raise GPIOException(f"Pin {self.pin_number} is not an output pin.")
            self.interface.gpio.write(self.pin_number, 0)

    def read(self):
        """
        Reads the current value of the pin
        """
        if isinstance(self.interface, GPIOInterface):
            return GPIO.input(self.pin_number)
        elif isinstance(self.interface, FT232RGPIOInterface):
            if self.direction != "input":
                raise GPIOException(f"Pin {self.pin_number} is not an input pin.")
            return self.interface.gpio.read(self.pin_number)

    def start_pwm(self, frequency, duty_cycle):
       """
        Starts PWM on the pin.

        Args:
            frequency: The frequency of the PWM signal.
            duty_cycle: The duty cycle of the PWM signal.
        """
        if isinstance(self.interface, GPIOInterface):
            if self.pwm is not None:
                raise GPIOException(f"Pin {self.pin_number} is already running a PWM.")
            self.pwm = GPIO.PWM(self.pin_number, frequency)
            self.pwm.start(duty_cycle)
        elif isinstance(self.interface, FT232RGPIOInterface):
            raise GPIOException("PWM is not supported on FT232R.")

    def stop_pwm(self):
        """
        Stops the PWM on the pin.
        """
        if isinstance(self.interface, GPIOInterface):
            if self.pwm is None:
                raise GPIOException(f"Pin {self.pin_number} is not running a PWM.")
            self.pwm.stop()
            self.pwm = None
        elif isinstance(self.interface, FT232RGPIOInterface):
            raise GPIOException("PWM is not supported on FT232R.")

    def add_interrupt(self, callback, edge=GPIO.BOTH, bouncetime=200):
        """
        Adds an interrupt detection on the pin and assigns a callback.

        Args:
            callback: The callback function to be called when an interrupt occurs.
            edge: The edge on which to detect the interrupt (GPIO.BOTH, GPIO.RISING or GPIO.FALLING)
            bouncetime: The debounce time in ms
        """
        if isinstance(self.interface, GPIOInterface):
            GPIO.add_event_detect(self.pin_number, edge, callback=callback, bouncetime=bouncetime)
        elif isinstance(self.interface, FT232RGPIOInterface):
            raise GPIOException("Interrupts are not supported on FT232R.")

    def remove_interrupt(self):
        """
        Removes the interrupt detection on the pin.
        """
        if isinstance(self.interface, GPIOInterface):
            GPIO.remove_event_detect(self.pin_number)
        elif isinstance(self.interface, FT232RGPIOInterface):
            raise GPIOException("Interrupts are not supported on FT232R.")

    def cleanup(self):
        """
        Cleans up the pin and sets it back to input mode.
        """
        if isinstance(self.interface, GPIOInterface):
            GPIO.cleanup(self.pin_number)
        # No pin-specific cleanup for FT232R.
