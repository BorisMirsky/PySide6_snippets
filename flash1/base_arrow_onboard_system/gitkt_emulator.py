import time
import sys
import json
from PySide6.QtCore import QObject, Signal, QTimerEvent
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QPushButton, QSpinBox, QWidget, QDoubleSpinBox, QLabel, QGroupBox)
from PySide6.QtCore import QIODevice
from PySide6.QtSerialPort import QSerialPort
from typing import Callable, Optional, List
from enum import Enum
import struct

from presentation.machine.units.com_port.ComPortUnits import ComPortControllerStreamOptions

class ComPortController(QObject):
    valueChanged: Signal = Signal()
    class ComPortControllerStage(Enum):
        WaitHeader = 0,
        WaitBody = 1,
        WaitCRC = 2
        
    def __init__(self, 
        stream: QSerialPort, 
        receive_options: ComPortControllerStreamOptions,
        send_options: ComPortControllerStreamOptions,
        sync_state_timeout: int = None,
        parent: Optional[QObject] = None    ) ->None:
        
        super().__init__(parent)
        self.__state: ComPortController = ComPortController.ComPortControllerStage.WaitHeader
        self.__stream: QSerialPort = stream
        
        self.__receive_header: bytes = receive_options.header
        self.__receive_elements: List[int] = [0] * receive_options.body_size
        self.__receive_body: bytes = b'0' * 2 * receive_options.body_size + b'0'    # Добавляем один байт управления дискретными выходами!!!
        self.__receive_crc: Callable[[bytes, bytes], bytes] = receive_options.crc_function
        
        self.__send_header: bytes = send_options.header
        self.__send_elements: List[int] = [0] * send_options.body_size
        self.__send_crc: Callable[[bytes, bytes], bytes] = send_options.crc_function
        if sync_state_timeout is not None:
            self.startTimer(sync_state_timeout)

        # self.__sync_state_timer = QTimer()
        self.__stream.readyRead.connect(self.__on_ready_read)
        # self.__sync_state_timer.timeout.connect(self.__on_sync_state)
        # self.__sync_state_timer.start(sync_state_timeout)
    
    # def timerEvent(self, event: QTimerEvent) -> None:
    #     super().timerEvent(event)
    #     # self.__on_sync_state()
    #     self.__on_ready_read()

    def send_package(self) ->None:
        self.__on_sync_state()
    def receive_get(self, index: int) ->int:
        return self.__receive_elements[index]
    def send_set(self, index: int, value: int) ->int:
        self.__send_elements[index] = value
    def send_get(self, index: int) ->int:
        return self.__send_elements[index]
        
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
        return struct.pack(f">{len(data)}H", *data)
    @staticmethod
    def __bytes_to_uint16_array(data: bytes):
        return list(struct.unpack(f"{len(data) // 2}H", data[:len(data) // 2 * 2]))


def as_signed_value(value: int) -> int:    
    return value if value <= 32767 else -1*(65536 - value)

def crc_function(header: bytes, data: bytes) ->bytes:
    return bytes( [ sum(bytes([header[0]]) + data) & 0xFF ] )

def create_controller(configuration: dict):
    serial_name = 'COM7'
    connection = QSerialPort(serial_name)        
    connection.setBaudRate(configuration['models']['connection']['baud_rate'])
    if not connection.open(QIODevice.OpenMode.ReadWrite):
        raise Exception(f"Unavailable com port for connection '{serial_name}'")
    
    # poll_timer = configuration['models']['connection'].get('poll_timer', 50)
    receive_count = 8
    send_count = 15
    controller = ComPortController(
        stream = connection,
        receive_options = ComPortControllerStreamOptions(bytes([0xAB]), receive_count, crc_function),
        send_options = ComPortControllerStreamOptions(bytes([0xAB]), send_count, crc_function),
        sync_state_timeout = None)
    return controller


if __name__ == '__main__':    
    config = json.load(open('./resources/config.json'))
    # receive_count = config['models']['connection']['receive_items_count']
    # send_count = config['models']['connection']['send_items_count']
    sensors_config = config['models']['sensors'].copy()
    controls_config = config['models']['controls'].copy()
    controls_config['enable_register'] = {'register_id': 0}

    app = QApplication(sys.argv)
    serial_controller = create_controller(config)

    # ===========================================================================================
    # Датчики
    # ===========================================================================================
    receive_code_widgets: dict[str, QSpinBox] = dict()
    receive_value_widgets: dict[str, QDoubleSpinBox] = dict()

    receive_elements_layout = QGridLayout()
    receive_elements_layout.addWidget(QLabel('Код'), 0, 1)
    receive_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
    
    row  = 1
    for name, params in sensors_config.items():
        receive_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)

        receive_code_spinbox = QSpinBox()
        receive_code_spinbox.setReadOnly(True)
        receive_code_spinbox.setRange(-65535, 65535)
        receive_code_widgets[name] = receive_code_spinbox
        receive_elements_layout.addWidget(receive_code_spinbox, row, 1)

        if params.get('projection_range', False):
            receive_value_spinbox = QDoubleSpinBox()
            receive_value_spinbox.setReadOnly(True)
            receive_value_spinbox.setRange(-65535, 65535)
            receive_value_widgets[name] = receive_value_spinbox        
            receive_elements_layout.addWidget(receive_value_spinbox, row, 2)
        row += 1

    def package_received() ->None:
        # print('package_received')
        # time.sleep(0.001)
        for name, params in sensors_config.items():       
            serial_controller.send_set(params['register_id'], receive_code_widgets[name].value())

        # serial_controller.send_set(12, 117)
        serial_controller.send_package()
        time.sleep(0.00001)
        
    serial_controller.valueChanged.connect(package_received)
    # serial_controller.valueChanged.connect(lambda: print('controller().valueChanged'))

    def push_pedal_handle() ->None:
        receive_code_widgets['discrete_signals'].setValue(117)
    def release_pedal_handle() ->None:
        receive_code_widgets['discrete_signals'].setValue(0)
    push_pedal_button = QPushButton('Нажать педаль')
    push_pedal_button.clicked.connect(push_pedal_handle)
    release_pedal_button = QPushButton('Отпустить педаль')
    release_pedal_button.clicked.connect(release_pedal_handle)

    # ====================================================================================================================== #
    # Управляющие элементы                                                                                                   #
    # ====================================================================================================================== #
    send_code_widgets: dict[str, QSpinBox] = dict()
    send_value_widgets: dict[str, QDoubleSpinBox] = dict()

    send_elements_layout = QGridLayout()
    # send_elements_layout.addWidget(QLabel('Управляющие элементы'), 0, 0)
    send_elements_layout.addWidget(QLabel('Код'), 0, 1)
    # send_elements_layout.addWidget(QLabel('Значение (мм)'), 0, 2)
    
    row  = 1
    for name, params in controls_config.items():
        send_elements_layout.addWidget(QLabel(name+f" ({str(params['register_id'])})"), row, 0)
        send_element_spin_box = QSpinBox()
        send_element_spin_box.setRange(0, 65535)
        send_code_widgets[name] = send_element_spin_box
        send_elements_layout.addWidget(send_element_spin_box, row, 1)

        # if params.get('projection_range', False):
        #     send_value_spinbox = QDoubleSpinBox()
        #     send_value_spinbox.setReadOnly(True)
        #     send_value_spinbox.setRange(-65535, 65535)
        #     send_value_widgets[name] = send_value_spinbox        
        #     send_elements_layout.addWidget(send_value_spinbox, row, 2)
        row += 1

    def write_elements_to_controller() ->None:
        print('Write elements to controller...')
        for name, params in controls_config.items():       
            # units.controls().get(name).write(send_code_widgets[name].value())
            serial_controller.send_set(params['register_id'], send_code_widgets[name].value())

    # units.controller_communication_allowed = True

    write_elements_button = QPushButton('Записать значения')
    write_elements_button.clicked.connect(write_elements_to_controller)


    # reload_config_button = QPushButton('Перечитать конфиг')
    # reload_config_button.clicked.connect(reload_config)

    sensors_groupbox = QGroupBox('Датчики')
    sensors_groupbox.setLayout(receive_elements_layout)
    controls_groupbox = QGroupBox('Управляющие элементы')
    controls_groupbox.setLayout(send_elements_layout)

    window = QWidget()
    
    mainLayout = QGridLayout()
    window.setLayout(mainLayout)
    mainLayout.addWidget(sensors_groupbox, 0, 0)
    mainLayout.addWidget(push_pedal_button, 1, 0)
    mainLayout.addWidget(release_pedal_button, 2, 0)
    mainLayout.addWidget(controls_groupbox, 0, 1)
    mainLayout.addWidget(write_elements_button, 1, 1)
    # mainLayout.setHorizontalSpacing(10)

    window.setWindowTitle('GITKT Emulator')
    window.show()
    sys.exit(app.exec())
