from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo

from PyQt6.QtCore import QIODeviceBase

from model.message_models import Message, MessageFormatException


class XBeeException(Exception):
    def __init__(self, message):
        self.message = message


class XBee:
    """ A class to represent an XBee wireless module. """

    def __init__(self, model):
        self.port = QSerialPort()
        self.model = model
        self.port.readyRead.connect(self._handle_read)
        self.connected = False
        self.message_started = False
        self.current_message = ""

    def start(self, port_name):
        """ Starts a connection to the given serial port."""
        if self.connected:
            raise XBeeException("XBee is already connected")
        
        # Attempt to connect to available ports if no connection is valid
        for avail in QSerialPortInfo.availablePorts():
            print("Trying port: ", avail.portName())
            if avail.portName() == port_name:
                try:
                    self.port.setPort(avail)
                    self.port.open(QIODeviceBase.OpenModeFlag.ReadWrite)
                    self.port.write("sCONNECT".encode())
                    # TODO: Add more code for connection message/handling
                    self.connected = True
                    return
                except Exception as e:
                    raise XBeeException("Error while connecting to desired port")
                    
        raise XBeeException("Invalid port name")

    def stop(self):
        if not self.connected:
            raise XBeeException("XBee is not connected")
        
        self.port.close()
        self.connected = False


    @staticmethod
    def port_info():
        return [(p.portName(), p.description()) for p in QSerialPortInfo.availablePorts()]

    def _handle_read(self):
        buf = self.port.readAll()
        msgs = buf.data().decode()
        print("-----------")
        print(msgs)
        msgs = msgs.split(Message.start_token) # split messages received in same bunch

        # Discard a message if we haven't received the start token
        if not self.message_started and len(msgs[0]) > 0 and msgs[0][0] != "s":
            msgs.pop(0)

        # Handle all messages
        for i in range(len(msgs)):
            # Only append the msg if its the first and one has been started
            if i == 0 and self.message_started:
                self.current_message += msgs[i]
            else:
                self.message_started = True
                self.current_message = msgs[i]

            # Try to parse the current message and add to model
            try:
                print(self.current_message)
                timestamp, id, length, data = Message.parse_message(self.current_message)
                self.model.addMessage(timestamp, id, length, data)
                self.message_started = False
            except MessageFormatException as mfe:
                # Status of 0 means more data is needed, other means an error
                if mfe.status != 0:
                    print(mfe.message)
                    self.message_started = False
                


    def send_data(self, data):
        # if self._ser.is_open == False:
        #     raise XBeeException("Serial port is not open")
        # try:
        #     self._ser.write(data.encode('utf-8'))
        # except SerialTimeoutException as ste:
        #     raise XBeeException("Error writing the data")
        pass # TODO: implement

