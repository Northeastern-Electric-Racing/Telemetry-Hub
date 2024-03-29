from datetime import datetime
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt6.QtCore import QIODeviceBase

from ner_processing.message import Message, MessageFormatException
from ner_live.live_input import LiveInput, LiveInputException, InputState
from ner_telhub.model.message_model import MessageModel


class Candapter(LiveInput):
    """
    A class to represent a Candapter connection as a live input.
    """

    END_COMMAND = "\r".encode()
    SETUP_COMMAND = "S8".encode()
    OPEN_COMMAND = "O".encode()
    CLOSE_COMMAND = "C".encode()
    TIMEON_COMMAND = "A1".encode()
    START_TOKEN = "T".encode()

    def __init__(self, model: MessageModel):
        """
        Initialize the serial port and message handling variables.
        """
        super().__init__(model)
        self._reset()

    def _reset(self) -> None:
        """
        Resets this Candapter.
        """
        self.port = QSerialPort()
        self.port.setBaudRate(QSerialPort.BaudRate.Baud115200.value)
        self.port.setFlowControl(QSerialPort.FlowControl.HardwareControl)
        self.port.readyRead.connect(self._handle_read)
        self.message_started = False
        self.current_message = ""
        self.state = InputState.NONE
        self.error_count = 0
        self.success_count = 0

    def _validateState(self, desired_state: InputState) -> None:
        """
        Validates states and throws appropriate error messages.
        """
        if desired_state == InputState.NONE and self.state != InputState.NONE:
            raise LiveInputException("CANdapter is already connected.")
        elif desired_state == InputState.CONNECTED:
            if self.state == InputState.NONE:
                raise LiveInputException("CANdapter is not yet connected.")
            elif self.state == InputState.STARTED:
                raise LiveInputException("CANdapter has already started.")
        elif desired_state == InputState.STARTED:
            if self.state == InputState.NONE:
                raise LiveInputException("CANdapter is not yet connected.")
            elif self.state == InputState.CONNECTED:
                raise LiveInputException("CANdapter has not yet been started.")

    def connect(self, *args, **kwargs) -> None:
        """
        Overrides LiveInput.connect()
        """
        self._validateState(InputState.NONE)

        if len(args) != 1:
            raise TypeError("Missing port name argument.")
        if not isinstance(args[0], str):
            raise TypeError("Invalid input type for port name.")
        port_name = args[0]

        for port in QSerialPortInfo.availablePorts():
            if port.portName() == port_name:
                try:
                    self.port.setPort(port)
                    self.state = InputState.CONNECTED
                    return
                except Exception as e:
                    raise LiveInputException(
                        "Error while connecting to desired port")
        raise LiveInputException("Invalid port name")

    def disconnect(self, *args, **kwargs) -> None:
        """
        Overrides LiveInput.disconnect()
        """
        self._validateState(InputState.CONNECTED)
        self._reset()

    def start(self, *args, **kwargs) -> None:
        """
        Overrides LiveInput.start()
        """
        self._validateState(InputState.CONNECTED)
        self.port.open(QIODeviceBase.OpenModeFlag.ReadWrite)
        self.port.write(self.SETUP_COMMAND)
        self.port.write(self.END_COMMAND)
        self.port.write(self.TIMEON_COMMAND)
        self.port.write(self.END_COMMAND)
        self.port.write(self.OPEN_COMMAND)
        self.port.write(self.END_COMMAND)
        self.state = InputState.STARTED

    def stop(self) -> None:
        """
        Overrides LiveInput.stop()
        """
        self._validateState(InputState.STARTED)
        self.port.write(self.CLOSE_COMMAND)
        self.port.write(self.END_COMMAND)
        self.port.close()
        self.state = InputState.CONNECTED

    def parse(self, message: str) -> Message:
        """
        Overrides LiveInput.parse().

        Format: 3CF1014521 - iiiLddtttt
            - iii = id
            - L = length
            - dd = L data bytes each with 2 chars
            - tttt = time stamp
        """
        try:
            id = int(message[0:3], base=16)
            length = int(message[3])
            data = []
            for i in range(length):
                data.append(int(message[(4 + 2 * i):(6 + 2 * i)], base=16))
            timestamp = datetime.fromtimestamp(
                float(message[(length * 2 + 4):]) / 1000)
            return Message(timestamp, id, data)
        except BaseException:
            raise MessageFormatException("Error with message fields")

    def _handle_read(self):
        """
        Handles the reading of Candapter data.
        """
        try:
            buf = self.port.readAll()
            msgs = buf.data().decode()
        except BaseException:
            print("Error with receiving message")
            return

        for char in msgs:
            if char == self.START_TOKEN.decode():
                self.message_started = True
                self.current_message = ""
            elif char == self.END_COMMAND.decode():
                try:
                    msg = self.parse(self.current_message)
                    if msg is not None:
                        self._model.addMessage(msg)
                    self.success_count += 1
                except MessageFormatException:
                    self.error_count += 1
                except RuntimeError:
                    self.stop()
                self.message_started = False
                self.current_message = ""
            elif self.message_started:
                self.current_message += char
