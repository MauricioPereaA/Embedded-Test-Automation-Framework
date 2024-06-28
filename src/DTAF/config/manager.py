# -*- coding: utf-8 -*-
import pathlib
from typing import Any
from weakref import proxy
from copy import copy, deepcopy
import toml
import traceback

G_error_messages: list[str] = [
    "<ERROR REPORT> --- --- ---\nERROR:\t{error}\nTYPE:\t{error_type}\nTRACEBACK:\n{tb}\n</END>"  # 0
    "Error: Section Name not found in Configuration, Section={section}.",  # 1
    "Error: Entry Name not found in Section, Section={section}, Entry={entry}.",  # 2
    "Error: Initial Data error, unable to build from schema. Schema={initial_data}"  # 3
    "Error: Missing Section Name Argument.",  # 4
    "Error: Missing Entry Name Argument."  # 5
    "Error: Unable to Add New Section: Section={section}.",  # 6
    "Error: Unable to add New Entry to Section: Section={section}, Entry={entry}.",  # 7
    "Error: Section Name Already in use. Section={section}",  # 8
    "Error: Entry Name already in use. Section={section}, Entry={entry}.",  # 9
    "Error: Filename's Parent path doesn't Exists: path={path}."  # 10
    "Error: Unable to update Entry Value: Section={section}, Entry={entry}.",  # 11
    "Error: Unable to open path. Access may be denied: path={path}."  # 12
    "Error: Configuration File Doesn't Exists: path={path}.",  # 13
    "Error: Path is a folder: path={path}.",  # 14
    "Error: Path is a file: path={path}.",  # 15
    "Error: Path Doesn't Exists: path={path}.",  # 16
    "Error: Unable to load configuration file: path={path}",  # 17
    "Error: Unable to unlink section entries: Section={section}",  # 18
    "Error: Missing parameter(s): parameters={parameters}",  # 19
]


def error_formatter(error: Exception, trace_back: str = "Not Provided.") -> str:
    msg: str = G_error_messages[0].format(error=error, error_type=type(error), tb=trace_back)
    return msg


class ConfigEntry:
    """
    Entry object abstraction.
    This class represents what a configuration entry is, how it will interact,
    and in the best case scenario, dispatches an update to the emulator to
    modify the behavior in real time (To Be Added).
    """

    name: str = ""
    """
    Configuration's Section Entry Name.
    This must be a human readable string.
    """

    __value = None
    """
    Value of the entry.
    """

    @property
    def value(self):
        return self.__value

    __section: proxy = None
    """
    Reference to the section this entry belongs to.

    This value must be set by the section this instance will be stored in.
    """

    flag_deep_copy: bool = False

    @property
    def section(self):
        """
        returns the section's proxy object.
        """
        return self.__section

    def __init__(
        self,
        name: str,
        section: proxy = None,
        value: Any = None,
        deep_copy_value: bool = False,
    ) -> None:
        """
        Initialization method.
        name: str
        Name of the entry.

        section: weakref.proxy -> ConfigSection = None
            Reference to the section object.

        value: Any = None
            Value to be assigned to the entry.

        deep_copy_value: bool = False
            Behavior Flag.
            Set True to make a deep copy of the value parsed (copy.deepcopy).
            Set False to make a simple Copy (copy.copy).


        """
        self.__section = proxy(section)
        self.name = name
        if deep_copy_value:
            self.__value = deepcopy(value)
            self.flag_deep_copy = True
        else:
            self.__value = copy(value)
            self.flag_deep_copy = False

    def set_value(self, value: Any):
        self.__value = value
        return True
        pass


class ConfigSection:
    """
    Configuration Section.

    This object will represent a Configuration Section in memory.
    """

    name: str = ""
    "Name of the section"

    __store: dict = None
    """
    Data Storage.

    Here we will store all configuration entries in a safe, Read only for
    external clients, and RW for internal methods.

    The idea is that only the class can modify and see this attr.
    """

    entries: set = None
    """
    Returns a list of keys from __store.

    Each one the name of a configuration entry.
    """

    @property
    def entries(self) -> set:
        return set(self.__store.keys())

    def __init__(self, name: str = "", initial_data: dict = {}) -> None:
        self.__store = {}
        if not name:
            raise ValueError(G_error_messages[4]
                             # "Missing Section Name in arguments."
                             )
        self.name = name
        check: bool = False
        for entry in initial_data:
            check = self.add_entry(entry, initial_data[entry])
            if check is False:
                raise ValueError(G_error_messages[7].format(section=self.name, entry=entry)
                                 # f"Unable to add new entry to section: Entry={entry}, Section={self.name}"
                                 )

    def add_entry(self, entry_name: str, value: Any) -> bool:
        """
        Adds a new entry to the configuration Section.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        if entry_name in self.__store:
            return False
        self.__store[entry_name] = ConfigEntry(name=entry_name, value=value, section=self)
        return True

    def delete_entry(self, entry_name: str) -> bool:
        """
        Deletes the configuration entry from the section given.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        if entry_name not in self.__store:
            return False
        del self.__store[entry_name]
        return True

    def get_entry(self, entry_name: str) -> Any:
        if entry_name not in self.__store:
            raise ValueError(G_error_messages[2].format(section=self.name, entry=entry_name)
                             # f"Entry name not found in section, Section={self.name}, "
                             # f"Entry={entry_name}"
                             )
        return self.__store[entry_name].value

    def get_entry_object(self, entry_name: str) -> ConfigEntry:
        if entry_name not in self.__store:
            raise ValueError(G_error_messages[2].format(section=self.name, entry=entry_name))
        return self.__store[entry_name]

    def update_entry(self, entry_name: str, value: Any) -> bool:
        entry = self.get_entry_object(entry_name)
        check: bool = entry.set_value(value)
        if check is False:
            raise ValueError(G_error_messages[2].format(section=self.name, entry=entry_name))
        return True

    def unlink_entries(self):
        """
        Cleaning method.

        This method must be called once we want to discard the section from
        memory, so we can collect the section with the garbage collector (gc).

        This method will unlink all entires from the section.
        """
        for entry in list(self.__store.keys()):
            del self.__store[entry]

    def collect_data(self) -> dict:
        """
        Collects all values and names from each entry.

        This method is inteded to be used to download all data into a file.
        Each entry and value will be returned as a dictionary.
        """
        data: dict = {}
        for entry in self.__store:
            data[entry] = self.__store[entry].value
        return data

    def __getattr__(self, attr: str):
        if attr in self.__store:
            return self.__store[attr].value


class ConfigManager:
    __store: dict = {}
    """
    Data Storage.

    Here we will store all configurations in a safe Read only for external
    clients, and RW for internal methods.

    The idea is that only the class can modify and see this attr.
    """

    __filename: str | pathlib.Path = None

    @property
    def filename(self) -> pathlib.Path:
        return self.__filename

    @property
    def sections(self, ) -> set:
        """
        List of keys to read from.

        This section keys are taken from __store, and returned as a set
        """
        return set(self.__store.keys())

    def __init__(self, filename: str | pathlib.Path):
        """
        Initialization method.
        """
        if not filename:
            raise ValueError(G_error_messages[19].format(paramter="filename"))
        filename = pathlib.Path(filename)
        if filename.exists() is False:
            if filename.parent.exists() is True:
                self.dump(filename=filename)
            else:
                raise FileNotFoundError(G_error_messages[16].format(path=filename.parent)
                                        # f"Parent folder of the provided filename doesn't exitst {filename.parent}"
                                        )
        self.__filename = filename
        self.loads(filename=filename)

    def add_section(self, section_name: str, initial_data: dict = {}) -> bool:
        """
        Adds a new section to the configuration structure.

        Returns True if the task succeeded, otherwise, it will return False
        """
        if section_name in self.__store:
            # TODO: add error log here.
            raise ValueError(
                G_error_messages[8].format(section=section_name)
                # f"Unable to add new section, name is already in use. name={name}, "
                # f"initial_data=\n{initial_data}</END>"
            )
            return False
        self.__store[section_name] = ConfigSection(name=section_name, initial_data=initial_data)
        return True

    def add_entry(self, section_name: str, entry_name: str, value: Any = None):
        """
        Adds a new entry to the configuration Section.
        """
        check: bool = False
        section: ConfigSection = None
        # Verify the section exists.
        section = self.get_section(section_name)
        # Verify the entry name is not already in use.
        if entry_name in section_name.entries:
            raise ValueError(G_error_messages[9].format(entry=entry_name, section=section_name)
                             # f"Entry already present in section. Section: {section_name}, "
                             # f"Entry: {entry_name}"
                             )
        # adds entry to section
        check = section.add_entry(entry_name, value)
        if check is False:
            raise RuntimeError(
                G_error_messages[7].format(section=section_name, entry=entry_name)
                # f"Unable to add new entry to section.Section: {section_name}, "
                # f"Entry: {entry_name}"
            )
        pass

    def update_entry(self, section_name: str, entry_name: str, value: Any) -> bool:
        """
        Updates an entry from a Section.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        section: ConfigSection = self.get_section(section_name)
        entry = section.get_entry(entry_name)
        check: bool = entry.set_value(value)
        if check is False:
            raise ValueError(G_error_messages[11].format(section=section_name, entry=entry_name))
        return True

    def delete_entry(self, section_name: str, entry_name: str) -> bool:
        """
        Deletes the configuration entry from the section given.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        section: ConfigSection = self.get_section(section_name)
        section.delete_entry(entry_name)
        return True

    def delete_section(self, section_name: str) -> bool:
        """
        Removes a section from the configuration.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        check: bool = False
        if section_name not in self.__store:
            raise ValueError(G_error_messages[1].format(section=section_name))
            # raise ValueError(f"Section name not in configuration. Section={name}")
            return False

        # unlink all entries from the section.
        check = self.__store[section_name].unlink_entries()
        if check is False:
            raise MemoryError(G_error_messages[18].format(section=section_name))
            # raise MemoryError("Unable to unlink all entries from section")
            return False

        # Deletes entry from storage.
        del self.__store[section_name]
        return True

    def loads(self, filename: str) -> bool:
        """
        Configuration Manager Loader method.

        This method will take the path provided and load it's configurations.
        Returns True if the task succeeded, otherwise, it will return False
        """
        path: pathlib.Path = pathlib.Path(filename)
        check: bool = False
        if path.parent.exists() is False:
            raise FileExistsError(G_error_messages[13].format(path=filename)
                                  # f"Cofniguration file doesn't exists: path={path}"
                                  )

        # Check that we're able to load the toml config file.
        try:
            with open(path, "r") as file:
                data = toml.loads(file.read())
        except Exception as error:
            # TODO: ADD ERROR LOGGER HERE.
            msg: str = "\n".join((
                G_error_messages[17].format(path=filename),
                error_formatter(error, trace_back=traceback.format_exc()),
            ))
            raise IOError(msg)
            # print(f"ERROR:\n\t{error}\nTRACEBACK:\n{traceback.format_exc()}")
            return False

        # load each section in memory.
        for section in data:
            # TODO: Add logger trace here
            print(f"TRACE: Adding new section {section}")
            check = self.add_section(section_name=section, initial_data=data[section])
            if check is False:
                raise ValueError(G_error_messages[3].format(initial_data=f"section[{section}]:{data[section]}"))
        return True

    def dumps(self) -> dict:
        """
        Returns a plain copy of all the contents as a dictionary.
        """
        data: dict = {}
        for section in self.__store:
            data[section] = self.__store[section].collect_data()
        return data

    def dump(self, filename: str | pathlib.Path) -> bool:
        """
        Dumps current memory frame into a file for storage.

        Returns True if the task succeeded, otherwise, it will return False.
        """
        data: dict = {}
        data = self.dumps()
        filename: pathlib.Path = pathlib.Path(filename)
        if filename.is_dir():
            raise IsADirectoryError(G_error_messages[14].format(path=filename)
                                    # f"Invalid filename. the Path is a folder, not a file. path={filename}"
                                    )
        if filename.parent.exists() is False:
            raise FileNotFoundError(G_error_messages[10].format(path=filename.parent)
                                    # f"Parent Path doesn't exitst. path={filename.parent}"
                                    )
        try:
            with open(filename, "w") as file:
                toml.dump(data, file)
        except Exception as error:
            # TODO: Add error logger here.
            msg: str = "\n".join((
                G_error_messages[12].format(path=filename),
                error_formatter(error, trace_back=traceback.format_exc()),
            ))
            raise IOError(msg)
        return True

    def __getattr__(self, attr: str):
        """
        Defines the primitive method to retrieve the object's attributes.

        This mod will allow us to retrieve names from __store and access them
        as attributes.
        """
        if attr in self.__store:
            return self.__store[attr]

    def get_section(self, section_name: str):
        """
        Gets the Configuration's Section by Name.
        """
        if section_name not in self.__store:
            raise ValueError(G_error_messages[1].format(section=section_name)
                             # f"Section name not found in Configuration. Section={section_name}"
                             )
        return self.__store[section_name]

    def get_entry(self, section_name: str, entry_name: str) -> Any:
        """
        Gets the configuration's Entry provided by Section.
        """
        section = self.get_section(section_name)
        return section.get_entry(entry_name)

        pass
