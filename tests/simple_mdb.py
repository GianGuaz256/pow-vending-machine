import serial
ser = serial.Serial('/dev/ttyAMA0', 9600, timeout=1)
ser.write(b'\x00')  # Send RESET command
response = ser.read(1)  # Expect ACK (0x00)
print(f"Response: {response.hex()}")
ser.close()