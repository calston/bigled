import serial
import struct

ser = serial.Serial('/dev/ttyACM0')

buf = b"\x01"
for i in range(1280):
    buf+= b"\x00\x00\x00"

ser.write(buf)
