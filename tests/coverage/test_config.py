# -*- coding: utf-8 -*-
import pytest
import unittest
import pathlib

import DTAF
import DTAF.config.manager

#TODO: remove this block once our own logger has been added.
# temporal Logger
import logging

Logger = logging.getLogger("Test_Config")
# </END>

data: dict = {
    "configmanager": [
        "sections",
        "filename",
        "loads",
        "dump",
        "dumps",
        "update_entry",
        "add_section",
        "add_entry",
        "delete_section",
        "delete_entry",
        "get_entry",
    ],
    "configsection": [
        "entries",
        "name",
        "add_entry",
        "delete_entry",
        "update_entry",
        "get_entry",
        "unlink_entries",
        "collect_data",
    ],
    "configentry": [
        "name",
        "section",
        "value",
        "flag_deep_copy",
        "set_value",
    ],
}
sample_toml = """[sample]
test1 = "22"
test2 = 123
test3 = [ 1, 2, 3,]

[sample.test4]
test41 = "asdf1234"
"""


@pytest.mark.config_test
class TestManager(unittest.TestCase):

    def format_checks(self, key: str, attr: list[str], values: list[bool]) -> str:
        coverage: float = 100 * (sum((1 for n in values if n is True)) / len(values))
        values = (str(n) for n in values)
        msg: str = "\n".join(((f"{key}:\t" + "\t-\t".join(n)) for n in zip(values, attr)))
        msg += f"\nCoverage at: [{coverage}%]"
        return msg

    def test_ConfigManager_Attributes(self):
        Object = DTAF.config.manager.ConfigManager
        key: str = "configmanager"
        checks: list = [hasattr(Object, attr) for attr in data[key]]
        checks += [getattr(getattr(Object, attr), "__doc__") != "" for attr in data[key]]
        print(self.format_checks(key, data[key] + (["__doc__"] * len(data[key])), checks))
        self.assertNotIn(False, checks)


    def test_ConfigSection_Attributes(self):
        Object = DTAF.config.manager.ConfigSection
        key: str = "configsection"
        checks: list = [hasattr(Object, attr) for attr in data[key]]
        checks += [getattr(getattr(Object, attr), "__doc__") != "" for attr in data[key]]
        print(self.format_checks(key, data[key] + (["__doc__"] * len(data[key])), checks))
        self.assertNotIn(False, checks)

    def test_ConfigEntry_Attributes(self):
        Object = DTAF.config.manager.ConfigEntry
        key: str = "configentry"
        checks: list = [hasattr(Object, attr) for attr in data[key]]
        checks += [getattr(getattr(Object, attr), "__doc__") != "" for attr in data[key]]
        print(self.format_checks(key, data[key] + (["__doc__"] * len(data[key])), checks))
        self.assertNotIn(False, checks)

    def test_ConfigEntry_Behavior(self):
        """Test the behavior from the config entry class"""

        # Creates the mockup class
        class mock_section:
            test_val = 22

        # Stores the mockup and loads the entry class pointing to it.
        mockup_section = mock_section()
        entry: DTAF.config.manager.ConfigEntry = None
        entry = DTAF.config.manager.ConfigEntry(
            name="test_entry",
            section=mockup_section,
            deep_copy_value=False,
            value=False,
        )

        # Verify that the value is what it's supposed to be: FALSE
        self.assertEqual(entry.value, False)

        # update value and check it's stored.
        entry.set_value(22)
        self.assertEqual(entry.value, 22)

        # verify property and link.
        self.assertEqual(entry.flag_deep_copy, False)
        self.assertEqual(entry.section, mockup_section)
        self.assertEqual(entry.name, "test_entry")

    def test_ConfigSection_Behavior(self):
        schema = {"test1": {1, 2, 3}, "test2": 22, "test3": None, "test4": "sample"}
        section: DTAF.config.manager.ConfigSection = None
        section = DTAF.config.manager.ConfigSection(
            name="test_section",
            initial_data=schema,
        )
        self.assertEqual(section.entries, {"test1", "test2", "test3", "test4"})
        # asserts all values were created as objects.
        self.assertIsInstance(section.get_entry_object("test1"), DTAF.config.manager.ConfigEntry)
        self.assertIsInstance(section.get_entry_object("test2"), DTAF.config.manager.ConfigEntry)
        self.assertIsInstance(section.get_entry_object("test3"), DTAF.config.manager.ConfigEntry)
        self.assertIsInstance(section.get_entry_object("test4"), DTAF.config.manager.ConfigEntry)
        # Asserts values are stored correctly.
        self.assertEqual(section.get_entry("test1"), {1, 2, 3})
        self.assertEqual(section.get_entry("test2"), 22)
        self.assertEqual(section.get_entry("test3"), None)
        self.assertEqual(section.get_entry("test4"), "sample")

        # Verify data can be collected back.
        self.assertEqual(section.collect_data(), schema)

        # verify we can unlink values.
        section.unlink_entries()
        self.assertEqual(section.entries, set())

        # verify we can add entries.
        section.add_entry("test1", schema["test1"])
        self.assertEqual(section.get_entry("test1"), schema["test1"])

        # verify we can change an entry value.
        section.update_entry("test1", {1, 2, 3, 4})
        self.assertEqual(section.get_entry("test1"), {1, 2, 3, 4})

        # check we can access the entry by attr instead by key
        self.assertEqual(section.test1, {1, 2, 3, 4})

    def test_ConfigManager_Behavior(self):
        root = pathlib.Path(__file__).parent
        folder = root / "temp"
        folder.mkdir(parents=True, exist_ok=True)
        file = folder / "test.toml"
        with open(file, "w") as file_:
            file_.write(sample_toml)
        config = DTAF.config.manager.ConfigManager(file)
        # assert that the memory has been saved correctly
        self.assertEqual(config.sections, {"sample"})
        self.assertEqual(config.sample.entries, {"test1", "test2", "test3", "test4"})
        self.assertEqual(config.sample.test4, {"test41": "asdf1234"})
        config.sample.test4["test_add"] = "data added"
        config.dump(file)
        with open(file, "r") as file_:
            data = file_.read()
        self.assertEqual(data, sample_toml + """test_add = "data added"\n""")
        self.assertTrue(file.exists())
        file.unlink()
        self.assertFalse(file.exists())
