import pytest
import time
from DTAF.interfaces import SerialInterface
from DTAF.interfaces.base.serial_interface import SerialException

@pytest.mark.Test_serial
class TestSerialConnection:
    """Test class for SerialConnection module."""

    @pytest.fixture(scope='function')
    def connection(self):
        """Fixture that returns a SerialConnection object."""
        return SerialInterface(port='COM5', baudrate=9600, timeout=1)

    def test_constructor(self, connection):
        """Test constructor."""
        assert connection.port == 'COM5'
        assert connection.baudrate == 9600
        assert connection.timeout == 1

    def test_constructor_invalid_input(self):
        """Test constructor with invalid input."""
        with pytest.raises(ValueError):
            SerialInterface(port=123)
        with pytest.raises(ValueError):
            SerialInterface(baudrate='invalid')
        with pytest.raises(ValueError):
            SerialInterface(timeout=-1)

    def test_connect_disconnect(self, connection):
        """Test connect and disconnect methods."""
        connection.connect()
        assert connection.is_connected()
        connection.disconnect()
        assert not connection.is_connected()

    @pytest.mark.read
    def test_write_read(self, connection):
        """Test write and read methods."""
        connection.connect()
        data_to_send = 'Hello\n'
        connection.write(data_to_send)
        time.sleep(0.2)
        data_received = connection.read()
        assert data_received == b'ACK'
        connection.disconnect()

    def test_write_not_connected(self, connection):
        """Test write method with device not connected."""
        with pytest.raises(SerialException):
            connection.write(b'Hello, device!')

    def test_read_not_connected(self, connection):
        """Test read method with device not connected."""
        with pytest.raises(SerialException):
            connection.read()

    def test_write_error(self, connection):
        """Test write method with write error."""
        connection.connect()
        connection.serial.close()
        with pytest.raises(SerialException):
            connection.write(b'Hello, device!')

    def test_read_error(self, connection):
        """Test read method with read error."""
        connection.connect()
        connection.serial.close()
        with pytest.raises(SerialException):
            connection.read()
