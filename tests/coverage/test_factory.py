# -*- coding: utf-8 -*-
import unittest
import pytest
import weakref
import traceback
import inspect

#TODO: remove this block once our own logger has been added.
# temporal Logger
import logging

Logger = logging.getLogger("Test_Device")
Logger.setLevel("DEBUG")
# </END>

from DTAF.interfaces.interfaces import InterfaceBase
from DTAF.devices.device import DeviceBase
import DTAF.factory

# Defines the test pattern for coverage.
data: dict = {
    "Factory": [
        "classnames",
        "register",
        "unregister",
        "update_definition",
        "verify_class",
    ],
}


class DummyInterface(InterfaceBase):
    """
    Dummy Interface class to make tests.
    """
    pass


class DummyDevice(DeviceBase):
    """
    Dummy Device class to make tests.
    """
    pass


@pytest.mark.coverage
#@pytest.mark.flag_test
class TestFactory(unittest.TestCase):

    def format_checks(self, key: str, attr: list[str], values: list[bool]) -> str:
        # calculates the current coverage coeficient based upon the tests.
        coverage: float = 100 * (sum((1 for n in values if n is True)) / len(values))
        # colors the values and converst them in strings.
        values = ("\033" + ("[1;32m" if n is True else "[1;31m") + str(n) + "\033[0m" for n in values)
        msg: str = "\n".join(((f"{key}:\t" + "\t-\t".join(n)) for n in zip(values, attr)))
        msg += "\nCoverage at: [\033[1;34m {}% \033[0m]".format(str(coverage)[:5])
        return msg

    def test_Factory_coverage(self):
        """
        Tests the DeviceBase class attributes.
        """
        # ---- Set memories ----
        Object = DTAF.factory.Factory
        key: str = "Factory"
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
        Logger.warning(self.format_checks(key, headers, checks))
        # ---- assert checks ----
        self.assertNotIn(False, checks)

    def test_factory_behavior(self):
        Factory: object = DTAF.factory.Factory
        Factory2: object = None
        DummyDevice_: str = 'DummyDevice'
        DummyInterface_: str = "DummyInterface"
        # Tests dummy classes.
        self.assertTrue(issubclass(DummyDevice, DeviceBase))
        self.assertTrue(issubclass(DummyInterface, InterfaceBase))
        # Test we can only have one instance of Factory.
        try:
            Factory2 = DTAF.factory._Factory()
            self.assertTrue(False)
        except RuntimeError as error:
            self.assertTrue(True)
        # Test we can read from and to.
        self.assertIn("Device", Factory.classnames)
        # Tests that the factory registry works as expected.
        Factory.register(DummyInterface_, DummyInterface)
        Factory.register(DummyDevice_, DummyDevice)
        # verify the classes are inside the factory library.
        self.assertIn(DummyInterface_, Factory.classnames)
        self.assertIn(DummyDevice_, Factory.classnames)

        # Test getattr from factory to request classes directly.
        #
        # test we can require the class by attr name.
        Device_ = Factory.DummyDevice
        self.assertTrue(inspect.isclass(Device_))
        # Tests DummyDevice instance.
        Device = Device_()
        self.assertTrue(isinstance(Device, Factory.DummyDevice))

        # Tests we can unregister the device.
        Factory.unregister(DummyDevice_)
        self.assertNotIn(DummyDevice_, Factory.classnames)
        Factory.register(DummyDevice_, DummyDevice)

        # Tests we can update the class definition on registry.
        Factory.update_definition(DummyInterface_, DummyDevice)
        self.assertTrue(Factory.DummyInterface == DummyDevice)
        # Returns registry to normal.
        Factory.update_definition(DummyInterface_, DummyInterface)
        self.assertTrue(Factory.DummyInterface == DummyInterface)

        # Test we can get class by name.
        cls = Factory.get_class_by_name(DummyInterface_)
        self.assertTrue(issubclass(cls, (DeviceBase, InterfaceBase)))

        # Clean up memory.
        del Device
        del Device_
        del cls

        # Removes registry.
        Factory.unregister(DummyDevice_)
        Factory.unregister(DummyInterface_)
