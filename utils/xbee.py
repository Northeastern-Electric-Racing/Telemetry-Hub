from serial import Serial, SerialException, SerialTimeoutException


class XBeeException(Exception):
    def __init__(self, message):
        self.message = message


class XBee:
    """ A class to represent an XBee wireless module. """

    def __init__(self, port, baud):
        self._callbacks = []

        try:
            # TODO: Add timeouts so read and write calls are not blocking
            self._ser = Serial(port=port, baudrate=baud)
            self._ser.open()
        except SerialException as se:
            print(se)
            raise XBeeException("Could not initialize serial port")
    
    def send_data(self, data):
        if self._ser.is_open == False:
            raise XBeeException("Serial port is not open")
        try:
            self._ser.write(data.encode('utf-8'))
        except SerialTimeoutException as ste:
            raise XBeeException("Error writing the data")

    def receive_data(self):
        if self._ser.is_open == False:
            raise XBeeException("Serial port is not open")
        if self._ser.in_waiting > 0:
            data = self._ser.read_until('\n')
            return data
        return None

    def add_callback(self):
        pass

