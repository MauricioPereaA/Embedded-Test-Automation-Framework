# -*- coding: utf-8 -*-
"""
Base interface Classes
=======================

These are the base classes for all interfaces used in this project.

Use the classes described in this section to build new, more resilient and
better interfaces for all your needs.

"""
import platform
from DTAF import interfaces
from DTAF.interfaces import interfaces
from DTAF.interfaces.interfaces import InterfaceBase

system_name = platform.uname().system
__all = []

# imports and includes the value to __all__
from DTAF.interfaces.base.can_interface import CANInterface

__all.append("CANInterface")

# imports and includes the value to __all__
from DTAF.interfaces.base.ethernet_interface import EthernetInterface

__all.append("EthernetInterface")

# imports and includes the value to __all__
# Only for linux.
if system_name == "Linux":
    from DTAF.interfaces.base.i2c_interface import I2CInterface
    __all.append("I2CInterface")
else:

    class I2CInterface(InterfaceBase):
        pass


# imports and includes the value to __all__
from DTAF.interfaces.base.serial_interface import SerialInterface

__all.append("SerialInterface")

# imports and includes the value to __all__
if system_name == "Linux":
    from DTAF.interfaces.base.spi_interface import SPIInterface
else:

    class SPIInterface(InterfaceBase):
        pass


__all.append("SPIInterface")

# imports and includes the value to __all__
from DTAF.interfaces.base.ssh_interface import SSHInterface

__all.append("SSHInterface")

# imports and includes the value to __all__
from DTAF.interfaces.base.telnet_interface import TelnetInterface

__all.append("TelnetInterface")

# imports and includes the value to __all__
from DTAF.interfaces.base.bluetooth_interface import BluetoothInterface

__all.append("BluetoothInterface")

__all__ = tuple(__all)
