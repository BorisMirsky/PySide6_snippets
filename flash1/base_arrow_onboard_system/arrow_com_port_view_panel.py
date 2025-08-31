from PySide6.QtWidgets import QApplication, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QSpinBox, QWidget
from PySide6.QtCore import QTimerEvent, QIODevice, QObject, Signal
from PySide6.QtSerialPort import QSerialPort
from typing import TypeVar, Callable, Generic, Optional, List, Any
from dataclasses import dataclass
from enum import Enum
import argparse
import json
import struct
import sys
# =======================================================

UnitType = TypeVar('UnitGenericType')
class AbstractReadUnit(QObject, Generic[UnitType]):
    changed = Signal(Any)
    def __init__(self, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
    def read(self) ->UnitType:
        pass
class AbstractReadWriteUnit(AbstractReadUnit[UnitType]):
    def write(self, value: UnitType) ->None:
        pass

# =======================================================
@dataclass(frozen = True)
class ComPortControllerStreamOptions:
    header: bytes
    body_size: int
    crc_function: Callable[[bytes, bytes], bytes]
class ComPortController(QObject):
    valueChanged: Signal = Signal()
    class ComPortControllerStage(Enum):
        WaitHeader = 0,
        WaitBody = 1,
        WaitCRC = 2
        
    def __init__(self, stream: QSerialPort, 
        receive_options: ComPortControllerStreamOptions,
        send_options: ComPortControllerStreamOptions,
        sync_state_timeout: int,
        parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__state: ComPortController = ComPortController.ComPortControllerStage.WaitHeader
        self.__stream: QSerialPort = stream
        
        self.__receive_header: bytes = receive_options.header
        self.__receive_elements: List[int] = [0] * receive_options.body_size
        self.__receive_body: bytes = b'0' * 2 * receive_options.body_size
        self.__receive_crc: Callable[[bytes, bytes], bytes] = receive_options.crc_function
        
        self.__send_header: bytes = send_options.header
        self.__send_elements: List[int] = [0] * send_options.body_size
        self.__send_crc: Callable[[bytes, bytes], bytes] = send_options.crc_function
        self.__stream.readyRead.connect(self.__on_ready_read)
        self.startTimer(sync_state_timeout)

    def receive_get(self, index: int) ->int:
        return self.__receive_elements[index]
    def send_set(self, index: int, value: int) ->int:
        self.__send_elements[index] = value
    def send_get(self, index: int) ->int:
        return self.__send_elements[index]
    
    def timerEvent(self, event: QTimerEvent) -> None:
        super().timerEvent(event)
        self.__on_sync_state()
    def __on_sync_state(self) ->None:
        body = ComPortController.__uint16_array_to_bytes(self.__send_elements)
        self.__stream.write(self.__send_header + body +
            self.__send_crc(self.__send_header, body)
        )

    def __on_ready_read(self) ->None:
        match self.__state:
            case ComPortController.ComPortControllerStage.WaitHeader:
                self.__handle_wait_header()
            case ComPortController.ComPortControllerStage.WaitBody:
                self.__handle_wait_body()
            case ComPortController.ComPortControllerStage.WaitCRC:
                self.__handle_wait_crc()
            case _:
                self.__state = ComPortController.ComPortControllerStage.WaitHeader
    def __handle_wait_header(self) ->None:
        while self.__stream.bytesAvailable() >= len(self.__receive_header):
            for required_byte in self.__receive_header:
                if self.__stream.read(1)[0] != bytes([required_byte]):
                    break
            else:
                self.__state = ComPortController.ComPortControllerStage.WaitBody
                self.__handle_wait_body()
                break

    def __handle_wait_body(self) ->None:
        if self.__stream.bytesAvailable() < len(self.__receive_body):
            return

        self.__receive_body = self.__stream.read(len(self.__receive_body)).data()
        self.__state = ComPortController.ComPortControllerStage.WaitCRC
        self.__handle_wait_crc()
    def __handle_wait_crc(self) ->None:
        if self.__stream.bytesAvailable() < 1:
            return

        crc_byte = self.__stream.read(1)
        calculated_crc = self.__receive_crc(self.__receive_header, self.__receive_body)
        if crc_byte == calculated_crc:
            self.__receive_elements = ComPortController.__bytes_to_uint16_array(self.__receive_body)
            self.__state = ComPortController.ComPortControllerStage.WaitHeader
            self.valueChanged.emit()

    @staticmethod
    def __uint16_array_to_bytes(data: List[int]):
        return struct.pack(f"{len(data)}H", *data)
    @staticmethod
    def __bytes_to_uint16_array(data: bytes):
        return list(struct.unpack(f"{len(data) // 2}H", data))

class ComPortReadUnit(AbstractReadUnit[int]):
    def __init__(self, origin: ComPortController, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: ComPortController = origin
        self.__index: int = index
        self.__origin.valueChanged.connect(self.valueChanged)
    def read(self) ->int:
        return self.__origin.receive_get(self.__index)
class ComPortReadWriteUnit(AbstractReadWriteUnit[int]):
    def __init__(self, origin: ComPortController, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: ComPortController = origin
        self.__index: int = index
        self.__origin.valueChanged.connect(self.valueChanged)
    def write(self, value: int) ->int:
        return self.__origin.send_set(self.__index, int(value))
    def read(self) ->int:
        return self.__origin.send_get(self.__index)
# =======================================================

def calculate_crc_function(header: bytes, data: bytes) ->bytes:
    return bytes([((256 - (sum(bytes([header[1]]) + data) & 0xFF)) & 0xFF)])

# =======================================================

def uint(argument: str) ->int:
    """ Type function for argparse - a uint value"""
    try:
        result = int(argument)
    except ValueError:    
        raise argparse.ArgumentTypeError("Must be a integer number")
    if result < 0:
        raise argparse.ArgumentTypeError('Argument must be non negative')
    return result
def uint16_t(argument: str) ->int:
    """ Type function for argparse - a uint16_t value"""
    result = uint(argument)
    if result < 0 or result > 65535:
        raise argparse.ArgumentTypeError('Argument must be in range [0; 65535]')
    return result


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(prog = 'Arrow COM-port view panel', description = 'Receive and send arrow-com-port packages')
    args_parser.add_argument('--port', dest = 'port', required = True, type = str, help = 'Com port address') 
    args_parser.add_argument('--baud-rate', dest = 'baud_rate', required = True, type = lambda arg: QSerialPort.BaudRate[f'Baud{arg}'], help = 'Com port baud rate') 
    args_parser.add_argument('--receive-count', dest = 'receive_count', required = True, type = uint16_t, help = 'Receive elements (uint16_t) count') 
    args_parser.add_argument('--send-count', dest = 'send_count', required = True, type = uint16_t, help = 'Send elements (uint16_t) count') 
    args_parser.add_argument('--send-message-timeout', dest = 'send_message_timeout', default = 5, type = uint, help = 'Send message timeout (ms)') 
    args_parser.print_help()
    
    config = json.load(open('./resources/config.json'))
    receive_names = {params['register_id']: name for name, params in config['models']['sensors'].items()}
    send_names = {params['register_id']: name for name, params in config['models']['controls'].items()}
    send_names[0] = 'enable_register'
    # print(send_names)

    arguments = args_parser.parse_args()
    app = QApplication(sys.argv)

    connection = QSerialPort(arguments.port)
    connection.setBaudRate(arguments.baud_rate)
    if not connection.open(QIODevice.OpenMode.ReadWrite):
        raise Exception('Unavailable com port for connection')

    controller = ComPortController(stream = connection,
        receive_options = ComPortControllerStreamOptions(bytes([0x77, 0x55]), arguments.receive_count, calculate_crc_function),
        send_options = ComPortControllerStreamOptions(bytes([0x77, 0xE4]), arguments.send_count, calculate_crc_function),
        sync_state_timeout = arguments.send_message_timeout)

    receive_message_elements: List[QSpinBox] = []
    receive_message_elements_layout = QFormLayout()
    receive_message_elements_layout.addRow('Receive array', None)
    for index in range(arguments.receive_count):
        receive_element_spin_box = QSpinBox()
        receive_element_spin_box.setReadOnly(True)
        receive_element_spin_box.setRange(0, 65535)
        receive_message_elements.append(receive_element_spin_box)
        receive_message_elements_layout.addRow(f"{receive_names.get(index, 'Unknown')} ({str(index)})", receive_element_spin_box)
    

    send_message_elements: List[QSpinBox] = []
    send_message_elements_layout = QFormLayout()
    write_elements_button = QPushButton('Write elements')
    send_message_elements_layout.addRow('Send array', write_elements_button)
    for index in range(arguments.send_count):
        send_element_spin_box = QSpinBox()
        send_element_spin_box.setRange(0, 65535)
        send_message_elements.append(send_element_spin_box)
        send_message_elements_layout.addRow(f"{send_names.get(index, 'Unknown')} ({str(index)})", send_element_spin_box)


    def read_elements_from_controller() ->None:
        for index in range(len(receive_message_elements)):
            receive_message_elements[index].setValue(controller.receive_get(index))
    def write_elements_to_controller() ->None:
        print('Write elements to controller...')
        for index in range(len(send_message_elements)):
            controller.send_set(index, send_message_elements[index].value())

    write_elements_button.clicked.connect(write_elements_to_controller)
    controller.valueChanged.connect(read_elements_from_controller)


    window = QWidget()
    window.setLayout(QHBoxLayout())
    window.layout().addLayout(receive_message_elements_layout)
    window.layout().addLayout(send_message_elements_layout)
    window.show()
    sys.exit(app.exec())
