from PySide6.QtSerialBus import QModbusRtuSerialClient, QModbusClient, QModbusDevice, QModbusDataUnit, QModbusRequest, QModbusReply
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import QSpinBox, QPushButton, QApplication, QTableView, QTextEdit, QWidget, QLineEdit, QLabel, QVBoxLayout
from PySide6.QtGui import QPen, QBrush, QColor, QPainter, QPaintEvent, QMouseEvent
from PySide6.QtCore import QIODevice, QEventLoop, QDateTime, QObject, QPointF, QLineF, Signal, Qt
from PySide6.QtNetwork import QTcpServer, QTcpSocket, QHostAddress
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtGui import QStandardItemModel
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
import traceback
import functools
import datetime
import random

import uuid
import json
import time
import sys
import struct
from presentation.machine.units.com_port.ComPortUnits import ComPortController, ComPortControllerStreamOptions


def uint16_array_to_bytes(data: List[int]):
    return struct.pack(f"{len(data)}H", *data)
def bytes_to_uint16_array(data: bytes):
    return list(struct.unpack(f"{len(data) // 2}H", data))

def calculate_crc_function(header: bytes, data: bytes) ->bytes:
    return bytes([((256 - (sum(bytes([header[1]]) + data) & 0xFF)) & 0xFF)])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # print()
    connection = QSerialPort('COM11')        
    connection.setBaudRate(115200)
    if not connection.open(QIODevice.OpenMode.ReadWrite):
        raise Exception('Unavailable com port for connection')
    controller = ComPortController(connection,
        ComPortControllerStreamOptions(bytes([0x77, 0x55]), 18, calculate_crc_function),
        ComPortControllerStreamOptions(bytes([0x77, 0xE4]), 12, calculate_crc_function),
        5)
    # read_unit = ComPortReadUnit(self.__controller, 0)
    # read_write_unit = ComPortReadWriteUnit(self.__controller, 0)
    def print_controller_state(): 
        print(f'state: {[controller.receive_get(i) for i in range(18)]}')
    controller.valueChanged.connect(print_controller_state)

    send_message_edit1 = QSpinBox()
    send_message_edit1.valueChanged.connect(lambda: controller.send_set(5, send_message_edit1.value()))
    send_message_edit2 = QSpinBox()
    send_message_edit2.valueChanged.connect(lambda: controller.send_set(7, send_message_edit2.value()))

    # current_view_label = QLabel()
    # send_message_edit = QLineEdit()
    # send_message_button = QPushButton('Send message')
    # send_header_button = QPushButton('Send header')
    # send_body_button = QPushButton('Send body')
    # send_crc_button = QPushButton('Send crc')

    # def convert_text_input_to_bytes() -> bytes:
    #     return uint16_array_to_bytes([int(substring) for substring in send_message_edit.text().split(',')])
    # send_message_button.clicked.connect(lambda: stream.send_message(convert_text_input_to_bytes()))
    # send_header_button.clicked.connect(lambda: stream.send_header())
    # send_body_button.clicked.connect(lambda: stream.send_body(convert_text_input_to_bytes()))
    # send_crc_button.clicked.connect(lambda: stream.send_crc(convert_text_input_to_bytes()))

    window = QWidget()
    layout = QVBoxLayout()
    window.setLayout(layout)
    layout.addWidget(send_message_edit1)
    layout.addWidget(send_message_edit2)
    # layout.addWidget(send_message_button)
    # layout.addWidget(send_header_button)
    # layout.addWidget(send_body_button)
    # layout.addWidget(send_crc_button)





    window.show()


    sys.exit(app.exec())