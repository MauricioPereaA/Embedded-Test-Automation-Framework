# -*- coding: utf-8 -*-
import unittest
import pytest
import DTAF.interfaces.builder
import yaml
import pprint
import weakref

#TODO: remove this block once our own logger has been added.
# temporal Logger
import logging

Logger = logging.getLogger("Test_Builder")
Logger.setLevel("DEBUG")
# </END>

data: dict = {
    "BuilderClass": [
        "get_new_UID",
        "register_new_device",
        "register_new_interface",
        "call_garbage_collector",
        "verify_registry",
        "validate_string",
        "load_string",
        "load_file",
        "remove_interface_by_UID",
        "remove_interface_by_proxy",
        "remove_device_by_UID",
        "remove_device_by_proxy",
        "get_reference_by_UID",
        "get_UID_by_reference",
        "interfaces",
        "devices",
        "root",
        "_flag_initialized",
        "max_uid",
    ],
    "device_type": {
        "type": "device",
        "interfaces": "",
        "filename": "test_device.yaml",
    },
    "interface_type": {
        "type": "interface",
        "filename": "test_interface.yaml",
    },
    "globals": {"Builder", "__all__"}
}

sample_yaml_model: str = """
Device:
    name: "Device_0"
    custom_attr: "custom_value"
    description: "This is a sample device based on DeviceBase"
    id: 23
    interfaces:
        SerialInterface:
            name: SERIAL_0
        SerialInterface:
            name: SERIAL_1

"""


@pytest.mark.coverage
@pytest.mark.flag_test
class TestBuilder(unittest.TestCase):

    def format_checks(self, key: str, attr: list[str], values: list[bool]) -> str:
        # calculates the current coverage coeficient based upon the tests.
        coverage: float = 100 * (sum((1 for n in values if n is True)) / len(values))
        # colors the values and converst them in strings.
        values = ("\033" + ("[1;32m" if n is True else "[1;31m") + str(n) + "\033[0m" for n in values)
        msg: str = "\n".join(((f"{key}:\t" + "\t-\t".join(n)) for n in zip(values, attr)))
        msg += "\nCoverage at: [\033[1;34m {}% \033[0m]".format(str(coverage)[:5])
        return msg

    def test_BuilderBase_Attributes(self):
        """
        Tests the BuilderClass class attributes.
        """
        # ---- Set memories ----
        Object = DTAF.interfaces.builder.BuilderClass
        key: str = "BuilderClass"
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

    def test_BuilderModule_Attributes(self):
        """
        Tests the Builder module Global attributes.
        """
        checks: list[bool] = [hasattr(DTAF.interfaces.builder, attr) for attr in data["globals"]]
        print(self.format_checks("Globals", data["globals"], checks))
        self.assertNotIn(False, checks)

    def test_build_instance(self):
        model = yaml.load(sample_yaml_model, Loader=yaml.SafeLoader)
        model = model[list(model.keys())[0]]
        # Define variables
        Builder = DTAF.interfaces.builder.Builder
        # General Testing
        Device = Builder.load_string(sample_yaml_model)
        # Tests Load.
        self.assertIn(Device.uid, Builder.devices)
        # Tests all attributes.
        keys = [key for key in model if key.lower() != 'interfaces']
        values = []
        for key in keys:
            Logger.info(f"key: {key}")
            Logger.info(f"value {getattr(Device,key)}")
            values.append(getattr(Device, key))
        Logger.warning(pprint.pformat(dict(zip(keys, values))))
