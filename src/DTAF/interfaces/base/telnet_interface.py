# -*- coding: utf-8 -*-
import telnetlib
import time
from DTAF.interfaces.interfaces import InterfaceBase


class TelnetException(Exception):
    """Exception class for Telnet communication errors"""
    pass


class TelnetInterface(InterfaceBase):
    """Class to establish a Telnet connection with a server or device."""

    def __init__(
            self,
            # host: str, port: int = 23, timeout: float = 1
            **kwargs):
        """
        Constructor for TelnetInterface class.

        Args:
            host: Hostname or IP address of the Telnet server.
            port: Port number of the Telnet server (default 23).
            timeout: Timeout for read operations in seconds (default 1).

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        # sets the default value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["host"] = kwargs.get("host", '127.0.0.1')
        kwargs["port"] = kwargs.get("port", 23)
        kwargs["timeout"] = kwargs.get("timeout", 1)

        # Execute base class inheritance.
        super().__init__(**kwargs)

        if not isinstance(kwargs['host'], str):
            raise ValueError(f"Host must be a string, but got {type(kwargs['host'])} instead.")
        if not isinstance(kwargs['port'], int) or kwargs['port'] <= 0:
            raise ValueError(f"Port must be a positive integer, but got {kwargs['port']} instead.")
        if not isinstance(kwargs['timeout'], (float, int)) or kwargs['timeout'] <= 0:
            raise ValueError(f"Timeout must be a positive float or integer, but got {kwargs['timeout']} instead.")
        self.host = kwargs['host']
        self.port = kwargs['port']
        self.timeout = kwargs['timeout']
        self.telnet = None

    def connect_impl(self) -> None:
        """
        Connect to the Telnet server.

        Raises:
            TelnetException: If connection fails.

        Returns:
            None
        """
        if self.is_connected():
            return
        try:
            self.telnet = telnetlib.Telnet(self.host, self.port, self.timeout)
        except Exception as e:
            self.telnet = None
            raise TelnetException(f"Could not connect to {self.host}:{self.port}: {str(e)}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from the Telnet server.

        Returns:
            None
        """
        try:
            if self.is_connected():
                self.telnet.close()
                self.telnet = None
            else:
                raise TelnetException(f"Error disconecting from {self.host}")
        except Exception as e:
            raise TelnetException(f"Error disconecting from {self.host}: {str(e)}")

    def write_impl(self, data: bytes) -> None:
        """
        Write data to the Telnet server.

        Args:
            data: Data to write to the Telnet server.

        Raises:
            TelnetException: If write operation fails.

        Returns:
            None
        """
        if not self.is_connected():
            raise TelnetException(f"Cannot write to {self.host}:{self.port}, not connected.")
        try:
            self.telnet.write(data)
        except Exception as e:
            self.disconnect()
            raise TelnetException(f"Error writing data to {self.host}:{self.port}: {str(e)}")

    def read_impl(self) -> bytes:
        """
        Read data from the Telnet server.

        Raises:
            TelnetException: If read operation fails.

        Returns:
            Data read from the Telnet server.
        """
        if not self.is_connected():
            raise TelnetException(f"Cannot read from {self.host}:{self.port}, not connected.")
        try:
            return self.telnet.read_very_eager()
        except Exception as e:
            self.disconnect()
            raise TelnetException(f"Error reading data from {self.host}:{self.port}: {str(e)}") from e

    def read_until(self, match= b'/n', timeout=1):
        """
        Read data from the Telnet server until macth byte is found.

        Raises:
            TelnetException: If read operation fails.

        Returns:
            Data read from the Telnet server.
        """
        try:
            return self.telnet.read_until(match, timeout)
        except EOFError as error:
            raise


    def is_connected(self) -> bool:
        """
        Returns whether or not the Telnet connection is currently open.

        Returns:
            bool: True if the Telnet connection is open, False otherwise.
        """
        return self.telnet is not None


    def execute_command(self, command: str):
        """
        Execute a command on the Telnet server.

        Args:
            command: The command to be executed on the server.

        Raises:
            TelnetException: If write operation fails.

        Returns:
            The output of the command execution.
        """
        if not self.is_connected():
            raise TelnetException(f"Cannot execute command on {self.host}:{self.port}, not connected.")
        try:
            self.write_impl(command.encode('utf-8') + b'\n')
            time.sleep(2)  # give the server some time to execute the command and produce output
            return self.read_impl()
        except Exception as e:
            self.disconnect()
            raise TelnetException(f"Error executing command on {self.host}:{self.port}: {str(e)}")
