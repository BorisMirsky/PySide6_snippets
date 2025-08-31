from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from PySide6.QtCore import QObject, Signal, QTimerEvent
from PySide6.QtSerialPort import QSerialPort
from typing import Callable, Optional, List
from dataclasses import dataclass
from enum import Enum
import struct

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
        self.startTimer(sync_state_timeout)

        # self.__sync_state_timer = QTimer()
        self.__stream.readyRead.connect(self.__on_ready_read)
        # self.__sync_state_timer.timeout.connect(self.__on_sync_state)
        # self.__sync_state_timer.start(sync_state_timeout)
       
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
        # print(f'__on_ready_read.state={self.__state}')
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
                b = self.__stream.read(1)[0]
                # print(f'__handle_wait_header: {b}, required_byte={bytes([required_byte])}')
                if b != bytes([required_byte]):
                    break
            else:
                # print('SUCCESS HEADER READ!')
                self.__state = ComPortController.ComPortControllerStage.WaitBody
                self.__handle_wait_body()
                break

    def __handle_wait_body(self) ->None:
        if self.__stream.bytesAvailable() < len(self.__receive_body):
            return

        self.__receive_body = self.__stream.read(len(self.__receive_body)).data()
        # print(f'self.__receive_body={self.__receive_body}')
        # print(f"self.__receive_body=[{','.join([ '0x%02x' % b for b in self.__receive_body])}], len={len(self.__receive_body)}")
        # print(f"self.__receive_body_bytes_to_uint16={ComPortController.__bytes_to_uint16_array(self.__receive_body)}")
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
        # print(f'__uint16_array_to_bytes={data}')
        return struct.pack(f"{len(data)}H", *data)
    @staticmethod
    def __bytes_to_uint16_array(data: bytes):
        return list(struct.unpack(f"{len(data) // 2}H", data))


class ComPortReadUnit(AbstractReadUnit[int]):
    def __init__(self, origin: ComPortController, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: ComPortController = origin
        self.__index: int = index
        # self.__origin.valueChanged.connect(self.valueChanged)
        self.__origin.valueChanged.connect(lambda: self.changed.emit(self.read()))

    def read(self) ->int:
        return self.__origin.receive_get(self.__index)
   
class ComPortReadWriteUnit(AbstractReadWriteUnit[int]):
    def __init__(self, origin: ComPortController, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: ComPortController = origin
        self.__index: int = index
        # self.__origin.valueChanged.connect(self.valueChanged)
        self.__origin.valueChanged.connect(lambda: self.changed.emit(self.read()))

    def write(self, value: int) ->int:
        value = int(value)
        if value < 0:
            value = 65536 + value
        elif (value > 65535):
            value = 65535
        return self.__origin.send_set(self.__index, value)
    def read(self) ->int:
        return self.__origin.send_get(self.__index)

class SignedComPortReadUnit(ComPortReadUnit):
    def __init__(self, origin: ComPortController, index: int, parent: QObject):
        super().__init__(origin, index, parent)
        
    def __as_signed_value(self, value: int) -> int:    
        return value if value <= 32767 else -1 * (65536 - value)
    
    def read(self) ->int:
        return self.__as_signed_value(super().read())

