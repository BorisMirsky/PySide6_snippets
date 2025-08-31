import sys, os
from PySide6.QtSerialPort import *
from PySide6.QtCore import *


def serial_request(port: QSerialPort):
    port.write(
        b'\x2B\x20\x18\x1A\x00\x00\x12\x2e\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x02\x00\x02\x00\x02\x00\x02\x64')
    port.waitForBytesWritten()
    port.waitForReadyRead(50)
    print(port.readAll())


if __name__ == "__main__":
    app = QCoreApplication([])
    # for portInfo in QSerialPortInfo.availablePorts():
    #     print(portInfo.portName(), portInfo.systemLocation(), portInfo.serialNumber())
    port = QSerialPort("COM7")
    # QSerialPort("COM7")        -ТуцЦштвщц Windows
    # /dev/ttyUSBo (ttyUSB0 ?)   - Linux
    port.setBaudRate(QSerialPort.BaudRate.Baud115200)
    if not port.open(QIODevice.OpenModeFlag.ReadWrite):
        raise Exception("AIiajdlsakfj")

    port.readyRead.connect(lambda: print('in ready read'))

    timer = QTimer()
    timer.start(2000)
    timer.timeout.connect(lambda: serial_request(port))
    # QTimer.singleShot(1500, serial_request)
    sys.exit(app.exec())


