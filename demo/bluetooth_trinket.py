import board
import busio
import digitalio
import time

# Configuración del LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Configuración de UART
uart = busio.UART(board.TX, board.RX, baudrate=9600)

while True:
    if uart.in_waiting > 0:
        data = uart.read(1)  # Lee 1 byte

        if data is not None:
            data_string = "".join([chr(b) for b in data])

            if data_string == "1":
                led.value = True  # Enciende el LED
                uart.write(b'on\n')
            elif data_string == "0":
                led.value = False  # Apaga el LED
                uart.write(b'off\n')
            else:
                pass

    time.sleep(0.01)