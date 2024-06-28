# -*- coding: utf-8 -*-
import paramiko
from DTAF.interfaces.interfaces import InterfaceBase


class ConnectionError(Exception):
    """Exception raised for errors in the SSHConnection class."""


class SSHInterface(InterfaceBase):
    """Class to establish an SSH connection with a device."""

    def __init__(
            self,
            # hostname: str, port: int, username: str, password: str
            **kwargs):
        """
        Constructor for SSHConnection class.

        Args:
            hostname: Hostname or IP address of the device to connect to.
            port: Port number for the SSH connection.
            username: Username for the SSH connection.
            password: Password for the SSH connection.

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """
        # sets the deffault value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["hostname"] = kwargs.get("hostname", "192.168.1.83")
        kwargs["port"] = kwargs.get("port", 22)
        kwargs["username"] = kwargs.get("username", 'user')
        kwargs["password"] = kwargs.get("password", 'user')

        # Execute base class inheritance.
        super().__init__(**kwargs)

        if not isinstance(kwargs['hostname'], str):
            raise ValueError(f"Hostname must be a string, but got {type(kwargs['hostname'])} instead.")
        if not isinstance(kwargs['port'], int) or kwargs['port'] <= 0:
            raise ValueError(f"Port must be a positive integer, but got {kwargs['port']} instead.")
        if not isinstance(kwargs['username'], str):
            raise ValueError(f"Username must be a string, but got {type(kwargs['username'])} instead.")
        if not isinstance(kwargs['password'], str):
            raise ValueError(f"Password must be a string, but got {type(kwargs['password'])} instead.")
        self.hostname = kwargs['hostname']
        self.port = kwargs['port']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.client = None
        self.transport = None

    def connect_impl(self) -> None:
        """
        Connect to the device via SSH.

        Raises:
            ConnectionError: If connection fails.

        Returns:
            None
        """
        if self.is_connected():
            return
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, self.port, self.username, self.password)
            self.transport = self.client.get_transport()
        except paramiko.AuthenticationException as e:
            self.disconnect()
            raise ConnectionError(f"Authentication failed: {str(e)}")
        except paramiko.SSHException as e:
            self.disconnect()
            raise ConnectionError(f"Could not establish SSH connection: {str(e)}")
        except Exception as e:
            self.disconnect()
            raise ConnectionError(f"Error connecting to {self.hostname}:{self.port}: {str(e)}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from the device via SSH.

        Returns:
            None
        """
        if self.is_connected():
            self.client.close()
            self.client = None
            self.transport = None

    def execute(self, command: str) -> str:
        """
        Execute a command on the remote device.

        Args:
            command: Command to execute on the remote device.

        Raises:
            ConnectionError: If the command execution fails.

        Returns:
            The output of the command as a string.
        """
        if not self.is_connected():
            raise ConnectionError("Cannot execute command, not connected.")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if error:
                raise ConnectionError(error)
            return output
        except (paramiko.SSHException, ConnectionError) as e:
            self.disconnect()
            raise ConnectionError(f"Error executing command {command}: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if connection to the device is established.

        Returns:
            True if connected, False otherwise.
        """
        return self.client is not None
