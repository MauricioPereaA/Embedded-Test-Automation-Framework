# -*- coding: utf-8 -*-
# Initializes the interface base class.
from . import interfaces

# Initialiezes the interfaces base module.
import DTAF.interfaces.base

# Registers all interfaces in Factory.
import logging

Logger = logging.getLogger("Registry")

import DTAF
from DTAF.factory import Factory

from DTAF.devices.device import DeviceBase
from DTAF.interfaces.interfaces import InterfaceBase

try:
    # Registers the base classes.
    Factory.register("Device", DeviceBase)
    Factory.register("Interface", InterfaceBase)

    # Registers all interfaces.
    from DTAF.interfaces.base import (
        CANInterface,
        EthernetInterface,
        I2CInterface,
        SerialInterface,
        SPIInterface,
        SSHInterface,
        TelnetInterface,
        BluetoothInterface,
    )

    #Logger.info("Factory: Adding Specific interface Classes to registry.")
    Factory.register("CANInterface", CANInterface)
    Factory.register("EthernetInterface", EthernetInterface)
    Factory.register("I2CInterface", I2CInterface)
    Factory.register("SerialInterface", SerialInterface)
    Factory.register("SPIInterface", SPIInterface)
    Factory.register("SSHInterface", SSHInterface)
    Factory.register("TelnetInterface", TelnetInterface)
    Factory.register("BluetoothInterface", BluetoothInterface)
    Logger.info("Factory: Loaded all interfaces.")

except ValueError as error:
    pass
