# -*- coding: utf-8 -*-
import unittest
import pytest
import weakref
import traceback
# from DTAF.devices.device import DeviceBase
import DTAF.devices.device
import DTAF.interfaces.interfaces

#TODO: remove this block once our own logger has been added.
# temporal Logger
import logging

Logger = logging.getLogger("Test_Device")
# </END>

data: dict = {
    "DeviceBase": [
        "store",
        "add_interface",
        "remove_interface",
        "get_interfaces",
    ],
}


@pytest.mark.coverage
#@pytest.mark.flag_test
class TestDeviceBase(unittest.TestCase):

    def format_checks(self, key: str, attr: list[str], values: list[bool]) -> str:
        # calculates the current coverage coeficient based upon the tests.
        coverage: float = 100 * (sum((1 for n in values if n is True)) / len(values))
        # colors the values and converst them in strings.
        values = ("\033" + ("[1;32m" if n is True else "[1;31m") + str(n) + "\033[0m" for n in values)
        msg: str = "\n".join(((f"{key}:\t" + "\t-\t".join(n)) for n in zip(values, attr)))
        msg += "\nCoverage at: [\033[1;34m {}% \033[0m]".format(str(coverage)[:5])
        return msg

    def test_DeviceBase_coverage(self):
        """
        Tests the DeviceBase class attributes.
        """
        # ---- Set memories ----
        Object = DTAF.devices.device.DeviceBase
        key: str = "DeviceBase"
        headers: list[str] = []
        checks: list[bool] = []  # [hasattr(Object, attr) for attr in headers]
        # --- code ---
        for attr in data[key][:]:  # iters over headers
            # ---- add headers ----
            headers.append(attr)
            headers.append(attr + ".__doc__")
            # ---- adds the checkup ----
            n = hasattr(Object, attr)
            checks.append(n)  # chekced that attr is covered (present)
            # --- checks if attr has documentation (docstring) ---
            # 1. object has attr.
            if n is True:
                # 1.1 checks that doc is filled.
                n = getattr(getattr(Object, attr), "__doc__") not in ['', None]
            else:
                n = False
            checks.append(n)
        Logger.info(self.format_checks(key, headers, checks))
        # ---- assert checks ----
        self.assertNotIn(False, checks)

    def test_device_behavior(self):
        # creates the instances.
        Interface = DTAF.interfaces.interfaces.InterfaceBase()
        Interface_ref = weakref.proxy(Interface)
        Device = DTAF.devices.device.DeviceBase()
        retusl: bool
        Logger.info("Created Variables at memory.")

        # Add an interface to the memory.
        Device.add_interface("Interface_0", Interface_ref)

        # Tests that we have the interface in store.
        self.assertIn("Interface_0", Device.get_interfaces())
        Logger.info("Interface_0 found in memory.")

        #Tests getattr is working as expected.
        result = False
        try:
            Logger.info("Testing for interface 0 connection attribute")
            getattr(Device.Interface_0, "connection")
            result = True
        except Exception:
            Logger.error(
                f"unexpected error found.\n{traceback.format_exc()}\nValid interface names: {Device.interfaces}")
            result = False
        self.assertTrue(result)

        # Removes an interface from the memory.
        Device.remove_interface("Interface_0")
        self.assertNotIn("Interface_0", Device.get_interfaces())
        Logger.info("Interface_0 Removed Successfully.")
