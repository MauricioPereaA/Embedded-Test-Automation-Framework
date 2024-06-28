#!: python
import DTAF, pathlib, json
import time, unittest, pytest
from DTAF.interfaces.builder import Builder
from DTAF.logger import SystemLogger as Logger

root = pathlib.Path(__file__).parent
Device = Builder.load_file(root/"demo device model.yaml")

class Test(unittest.TestCase):

    def test_bluetooth(self):
        Device.BLE_0.connect()
        time.sleep(3)
        # turn on the device
        Device.BLE_0.write("1")
        time.sleep(0.1)
        message = Device.BLE_0.read()
        Logger.info(f'Message from bluetooth {message}')
        self.assertEqual(message, b"on")
        # turn off the device.
        Device.BLE_0.write("0")
        time.sleep(0.1)
        message = Device.BLE_0.read()
        Logger.info(f'Message from bluetooth {message}')
        self.assertEqual(message, b"off")
        Device.BLE_0.disconnect()

    def serial_message(self):
        command = "This is a sample message for Interface SERIAL_0\n"
        Device.SERIAL_0.write(command)
        time.sleep(1)
        Device.SERIAL_0.write(command)
        time.sleep(0.2)
        message = Device.SERIAL_0.read_line()
        Logger.info(f"The message from SERIAL_0 is {message}")
        self.assertEqual(message, b"Message: This is a sample message for Interface SERIAL_0")


    def serial_digital_pin(self):
        command = "DI,7\n"
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message = Device.SERIAL_0.read_line()
        self.assertEqual(message, b"0")
        Logger.info(f"Current PIN-7 value: {message}")

        # changes pin value.
        command = "DO,7,1"
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message = Device.SERIAL_0.read_line()
        self.assertEqual(message, b"ACK")

        # back to normal state pin value
        command = "DO,7,0"
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message = Device.SERIAL_0.read_line()
        self.assertEqual(message, b"ACK")


    def serial_servo_test(self):
        # moves forward the servo.
        command = "servo, 180\n"
        message = Device.SERIAL_0.write(command)
        time.sleep(1)
        message = Device.SERIAL_0.read_line()
        self.assertEqual(message, b"ACK")
        #input("Press enter to move the servo back...")


        # moves back the servo.
        command = "servo, 30\n"
        message = Device.SERIAL_0.write(command)
        time.sleep(1)
        message = Device.SERIAL_0.read_line()
        self.assertEqual(message, b"ACK")

        # set variables.
        structure = {
            "Procesador": "ATMEL MEGA2560",
            "Modelo de Unidad": "2560x333",
            "Version de Firmware": "2305.01.23",
            "Power State": "ON",
            "Status": "OK",
        }
        command: str = "$INFO\n"


        # requests info from device.
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message: bytes = Device.SERIAL_0.read_line()
        data = json.loads(message)
        # compares the structure with the response.
        for key in structure:
            self.assertIn(key, data)
            self.assertEqual(data[key], structure[key])
        self.assertTrue(True)


    def serial_analog_pin(self):
        command = "AN,0\n"
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message = Device.SERIAL_0.read_line()
        """ input(
            "Please change the potentiometer position in the device and then press Enter to continue..."
        )"""
        Device.SERIAL_0.write(command)
        time.sleep(0.1)
        message_2 = Device.SERIAL_0.read_line()
        self.assertNotEqual(message, message_2)
        Logger.info(f"Analog Reads: [{[message, message_2]}]")


    def test_serial(self):
        Device.SERIAL_0.connect()
        self.serial_message()
        self.serial_digital_pin()
        self.serial_analog_pin()
        self.serial_servo_test()
        Device.SERIAL_0.disconnect()

    def test_telnet(self):
        Device.TELNET_0.connect()
        command = b"This is a sample message for Interface TELNET_0"
        Device.TELNET_0.write(command)
        time.sleep(0.1)
        # Blocking.
        message = Device.TELNET_0.read_until()
        self.assertTrue(True if message else False)
        Device.TELNET_0.disconnect()