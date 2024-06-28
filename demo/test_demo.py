# General use imports
from pathlib import Path
import time
import json

# import DTAF
import DTAF

# import device builder
from DTAF.interfaces.builder import Builder

# Get working dir absolute path
root = Path(__file__).parent

# Create a new device from model file
device = Builder.load_file(root/"demo device model.yaml")

# Verify that the interface attributes are an interface class
print(device.SERIAL_0)
print(device.TELNET_0)
print(device.BLE_0)

'''
# Initialize the connection to Bluetooth Interface
print(f'Connecting to Bluetooth device HC-06 with Trinket M0')
device.BLE_0.connect()

# sends message to BLE_0 interface turn on LED13
input("Press Enter to continue...")

message = '1'
device.BLE_0.write(message)
time.sleep(0.1)
response = device.BLE_0.read()
print(f'Response from Bluetooth: {response}')
input("Press Enter to continue...")
# Turn off LED 13
message = '0'
device.BLE_0.write(message)
time.sleep(0.1)
response = device.BLE_0.read()
print(f'Response from Bluetooth: {response}')
input("Press Enter to continue...")
'''
# Initialize the connection to the interfaces Serial and Telnet
device.SERIAL_0.connect()
##device.TELNET_0.connect()

# Sends message to SERIAL_0 interface SIMPLE MESSAGE
message = 'This is a sample message for Interface SERIAL_0\n'
device.SERIAL_0.write(message)
time.sleep(1)
device.SERIAL_0.write(message)
time.sleep(0.2)

# Reads message from interface SERIAL_0
response = device.SERIAL_0.read_line()
print(f'The message from SERIAL_0 is {response}')
input("Press Enter to continue...")

# Read and active DigitalOutput status in SerialDevice Pin#7
message = 'DI,7\n'
device.SERIAL_0.write(message)
time.sleep(1)
response = device.SERIAL_0.read_line()
print(f'Status of PIN 7: {response}')
input("Press Enter to continue...")
message = 'DO,7,1\n'
device.SERIAL_0.write(message)
time.sleep(1)

# Read confirmation of DigitalOutput activation
response = device.SERIAL_0.read_line()
print(f'The message from SERIAL_0 is {response}')
input("Press Enter to continue...")

# Read again the status in SerilDevice Pin#7
message = 'DI,7\n'
device.SERIAL_0.write(message)
time.sleep(1)
response = device.SERIAL_0.read_line()
print(f'Status of PIN 7: {response}')
input("Press Enter to continue...")

# Read the value from AnalogInput in SerialDevice AN channel 0
message = 'AN,0\n'
device.SERIAL_0.write(message)
time.sleep(1)
response = device.SERIAL_0.read_line()
print(f'Status of AnalogInput 0: {response}')
input("Press Enter to continue...")

# Read again the value from AnalogInput in SerialDevice AN channel 0
message = 'AN,0\n'
device.SERIAL_0.write(message)
time.sleep(1)
response = device.SERIAL_0.read_line()
print(f'Status of AnalogInput 0: {response}')
input("Press Enter to continue...")

# Read SerialDevice information
message = '$INFO\n'
device.SERIAL_0.write(message)
time.sleep(1)
response = device.SERIAL_0.read_line()
json_object = json.loads(response)
json_formatted_str = json.dumps(json_object, indent=2)
print(f'SerialDevice INFO: {json_formatted_str}')
input("Press Enter to continue...")

# Send command to move servomotor in SerialDevice PWM 180
message = 'servo, 180\n'
device.SERIAL_0.write(message)
time.sleep(1)

# Read confirmation of servo command
response = device.SERIAL_0.read_line()
print(f'The message from SERIAL_0 is {response}')
input("Press Enter to continue...")

# Send command to move servomotor in SerialDevice PWM 30
message = 'servo, 30\n'
device.SERIAL_0.write(message)
time.sleep(1)

# Read confirmation of servo command
response = device.SERIAL_0.read_line()
print(f'The message from SERIAL_0 is {response}')
input("Press Enter to continue...")

# close the connection with SERIAL_0
device.SERIAL_0.disconnect()
'''
#Sends message to TELNET_0 interface
message = b'This is a sample message for Interface TELNET_0'
device.TELNET_0.write(message)

# Read message from interface TELNET_0
response = device.TELNET_0.read_until()
print(f'The message from TELNET_0 is {response}')

# close the connection with TELNET_0
device.TELNET_0.disconnect()

# close the connection with BLE_0
device.BLE_0.disconnect()
'''
