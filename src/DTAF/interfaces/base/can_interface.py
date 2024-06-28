# -*- coding: utf-8 -*-
import can
from DTAF.interfaces.interfaces import InterfaceBase


class CANInterface(InterfaceBase):
    """Class to establish a CAN connection with a device via CAN interface."""

    def __init__(
            self,
            # channel: str, bitrate: int = 250000
            **kwargs):
        """
        Constructor for CANConnection class.

        Args:
            channel: CAN channel to connect to. REQUIRED
            bitrate: Bitrate of the CAN connection in bits per second (default 250000) OPTIONAL.

        Raises:
            ValueError: If any of the input parameters are invalid.

        Returns:
            None
        """

        # sets the default value in kwargs to parse it to super().__init__(**kwargs)
        kwargs["channel"] = kwargs.get("channel", "vcan0")
        kwargs["bitrate"] = kwargs.get("bitrate", 250000)

        # Execute base class inheritance.
        super().__init__(**kwargs)
        if not isinstance(kwargs["channel"], str):
            raise ValueError(f"Channel name must be a string, but got {type(kwargs['channel'])} instead.")
        if not isinstance(kwargs["bitrate"], int) or kwargs["bitrate"] <= 0:
            raise ValueError(f"Bitrate must be a positive integer, but got {kwargs['bitrate']} instead.")
        self.channel = kwargs["channel"]
        self.bitrate = kwargs["bitrate"]
        self.bus = None

    def connect_impl(self) -> None:
        """
        Connect to the CAN channel.

        Raises:
            ConnectionError: If connection fails.

        Returns:
            None
        """
        if self.is_connected():
            return
        try:
            self.bus = can.interface.Bus(channel=self.channel, bitrate=self.bitrate)
        except can.CanError as e:
            self.bus = None
            raise ConnectionError(f"Could not connect to {self.channel}: {str(e)}")

    def disconnect_impl(self) -> None:
        """
        Disconnect from the CAN channel.

        Returns:
            None
        """
        if self.is_connected():
            self.bus.shutdown()
            self.bus = None

    def write_impl(self, message: str, arbitration_id: int) -> None:
        """
        Write a CAN message.

        Args:
            message: String representation of the CAN message to write.
            arbitration_id: Arbitration ID of the CAN message to write.

        Raises:
            ConnectionError: If write operation fails.

        Returns:
            None
        """
        if not self.is_connected():
            raise ConnectionError("Cannot write message, not connected.")
        try:
            message_obj = can.Message.from_string(message, arbitration_id=arbitration_id)
            self.bus.send(message_obj)
        except (can.CanError, ValueError) as e:
            self.disconnect()
            raise ConnectionError(f"Error writing message: {str(e)}")

    def read_impl(self, arbitration_id: int, timeout: float = None) -> can.Message:
        """
        Read a CAN message.

        Args:
            arbitration_id: Arbitration ID of the CAN message to read.
            timeout: Timeout for the read operation in seconds (default None).

        Raises:
            ConnectionError: If read operation fails.

        Returns:
            The received CAN message as a can.Message object.
        """
        if not self.is_connected():
            raise ConnectionError("Cannot read message, not connected.")
        try:
            message_obj = self.bus.recv(timeout=timeout)
            while message_obj.arbitration_id != arbitration_id:
                message_obj = self.bus.recv(timeout=timeout)
            return message_obj
        except can.CanError as e:
            self.disconnect()
            raise ConnectionError(f"Error reading message: {str(e)}")

    def is_connected(self) -> bool:
        """
        Check if connection to the CAN channel is established.

        Returns:
            True if connected, False otherwise.
        """
        return self.bus is not None
