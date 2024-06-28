import pytest
import time
from DTAF.interfaces import TelnetInterface
from DTAF.interfaces.base.telnet_interface import TelnetException

# Reemplaza con la dirección IP y el puerto de tu servidor Telnet de prueba
TEST_HOST = "127.0.0.1"
TEST_PORT = 23

@pytest.mark.Test_Telnet
class TestTelnetInterface:
    """Test class for TelnetInterface"""

    def test_connect_disconnect(self):
        connection = TelnetInterface(host=TEST_HOST, port=TEST_PORT)
        connection.connect()
        assert connection.is_connected()
        connection.disconnect()
        assert not connection.is_connected()


    def test_write_read(self):
        connection = TelnetInterface(host=TEST_HOST, port=TEST_PORT)
        connection.connect()

        test_message = b"Hello, Telnet!\n"
        connection.write(test_message)
        time.sleep(0.2)
        response = connection.read()

        expected_response = b"Hello, Telnet!"
        assert response == expected_response

        connection.disconnect()


    def test_read_not_connected(self):
        connection = TelnetInterface(host=TEST_HOST, port=TEST_PORT)
        with pytest.raises(TelnetException):
            connection.read()


    def test_write_not_connected(self):
        connection = TelnetInterface(host=TEST_HOST, port=TEST_PORT)
        with pytest.raises(TelnetException):
            connection.write(b"Test message")
