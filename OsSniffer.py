import sys
import serial
import glob

## Determine on which platform we are working and get a list of COM-ports available
#  @return result A lift of Serial-ports available on the platform
def OS_SerialPortList():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # Exclude current terminal using this on unix
        ports = glob.glob('/dev/tty[A-Za-z\d]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result