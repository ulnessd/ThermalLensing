import serial
import serial.tools.list_ports  # this import is necessary to access list_ports

# list all available ports
ports = serial.tools.list_ports.comports()

# check if any port is available
if ports:
    # get the device name (port name) of the first available port
    myport = ports[0].device

    # print the port name
    print(f"Using port: {myport}")

    # use the port name to open a serial connection and send a test signal
    ser = serial.Serial(port=myport, baudrate=10000, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    ser.write(b'\xFF')

    print("Toggle signal sent successfully")

else:
    print("No ports available")


