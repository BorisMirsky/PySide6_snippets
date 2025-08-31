from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from PySide6.QtSerialBus import QModbusDevice, QModbusClient, QModbusDataUnit, QModbusReply
from PySide6.QtCore import QObject, QTimer, Qt, Signal
from typing import List, Tuple, Optional
import traceback
import copy

#===========================================================================================
class InputRegisterArray(QObject):
    valueChanged: Signal = Signal()
    def __init__(self, connection: QModbusClient, server: int, register_start: int, register_count: int, timeout: int = 50, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__connection: QModbusClient = connection
        self.__server: int = server
        self.__register_start: int = register_start
        self.__register_count: int = register_count

        self.__data_buffer: List[int] = [None for _ in range(self.__register_count)]
        self.startTimer(timeout, Qt.TimerType.PreciseTimer)
        self.__internalStateReadRequest()

    def count(self) ->int:
        return len(self.__data_buffer)
    def read(self, index: int) ->int:
        return self.__data_buffer[index - self.__register_start]
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__internalStateReadRequest()
    def __internalStateReadRequest(self) ->None:
        read_request = QModbusDataUnit(QModbusDataUnit.RegisterType.InputRegisters, self.__register_start, len(self.__data_buffer))
        reply: QModbusReply = self.__connection.sendReadRequest(read_request, self.__server)
        if reply is None:
            self.__internalStateReadError('[Modbus protocol error]: [Invalid request]')
        elif reply.isFinished():
            reply.deleteLater()
            self.__internalStateReadError('[Modbus protocol error]: [Make broadcast request]')
        else:
            reply.finished.connect(lambda: self.__internalStateReadFinished(reply))
    def __internalStateReadFinished(self, reply: QModbusReply) ->None:
        reply.deleteLater()
        if reply.error() != QModbusDevice.Error.NoError:
            self.__internalStateReadError(f'[Modbus protocol error]: [{reply.errorString()}][{reply.error()}]')
            return

        result = reply.result()
        if result.valueCount() != len(self.__data_buffer):
            self.__internalStateReadError(f'[Read value error]: Invalid count of reply registers: [{result.valueCount()}]:[{len(self.__value)}]')
            return

        self.__data_buffer = reply.result().values()
        # print(self.__data_buffer)
        self.valueChanged.emit()
    def __internalStateReadError(self, error: str) ->None:
        print('[InputRegisterArray]', error)
        print(traceback.print_stack())
        self.__data_buffer = [None for _ in self.__data_buffer]
        self.valueChanged.emit()

class InputRegister(AbstractReadUnit[int]):
    def __init__(self, origin: InputRegisterArray, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: InputRegisterArray = origin
        self.__index: int = index
        self.__origin.valueChanged.connect(lambda: self.changed.emit(read()))

    def read(self) ->int:
        return self.__origin.read(self.__index)

class SignedInputRegister(InputRegister):
    def __init__(self, origin: InputRegisterArray, index: int, parent: QObject):
        super().__init__(origin, index, parent)
        
    def __as_signed_value(self, value: int) -> int:    
        return value if value <= 32767 else -1 * (65536 - value)
    
    def read(self) -> int:
        return self.__as_signed_value(super().read())
    
#===========================================================================================
class HoldingRegisterArray(QObject):
    valueChanged: Signal = Signal()
    def __init__(self, connection: QModbusClient, server: int, register_start: int, register_count: int, timeout: int = 50, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        
        self.__connection: QModbusClient = connection
        self.__server: int = server
        self.__register_start: int = register_start
        self.__register_count: int = register_count

        self.__data_buffer: List[int] = [None for _ in range(self.__register_count)]
        self.__syncronization_buffer: List[Tuple[int, int]] = []
        self.startTimer(timeout, Qt.TimerType.PreciseTimer)
        self.__internalStateWriteRequest()

    def count(self) ->int:
        return len(self.__data_buffer)
    def read(self, index: int) ->int:
        return self.__data_buffer[index - self.__register_start]
    def write(self, index: int, value: int) ->None:
        self.__syncronization_buffer.append((index - self.__register_start, value))
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__internalStateWriteRequest()
    #--------------------------------------------------------------------------
    def __internalStateWriteRequest(self) ->None:
        if len(self.__syncronization_buffer) == 0:
            self.__internalStateReadRequest()
            return

        write_registers = [0 if item is None else item for item in self.__data_buffer]
        for index, value in self.__syncronization_buffer:
            write_registers[index] = int(value)
        self.__syncronization_buffer.clear()

        request = QModbusDataUnit(QModbusDataUnit.RegisterType.HoldingRegisters, self.__register_start, write_registers)
        reply: QModbusReply = self.__connection.sendWriteRequest(request, self.__server)
        if reply is None:
            self.__internalStateWriteError('[Modbus protocol error]: [Invalid request]')
        elif reply.isFinished():
            reply.deleteLater()
            self.__internalStateWriteError('[Modbus protocol error]: [Make broadcast request]')
        else:
            reply.finished.connect(lambda: self.__internalStateWriteFinished(reply))
    def __internalStateWriteFinished(self, reply: QModbusReply) ->None:
        reply.deleteLater()
        if reply.error() != QModbusDevice.Error.NoError:
            self.__internalStateWriteError(f'[Modbus protocol error]: [{reply.errorString()}][{reply.error()}]')
        else:
            self.__internalStateReadRequest()
    def __internalStateWriteError(self, error: str) ->None:
        print('[HoldingRegisterArray][Write]', error)
        self.__internalStateReadRequest()
    #--------------------------------------------------------------------------
    def __internalStateReadRequest(self) ->None:
        request = QModbusDataUnit(QModbusDataUnit.RegisterType.HoldingRegisters, self.__register_start, len(self.__data_buffer))
        reply: QModbusReply = self.__connection.sendReadRequest(request, self.__server)
        if reply is None:
            self.__internalStateReadError('[Modbus protocol error]: [Invalid request]')
        elif reply.isFinished():
            reply.deleteLater()
            self.__internalStateReadError('[Modbus protocol error]: [Make broadcast request]')
        else:
            reply.finished.connect(lambda: self.__internalStateReadFinished(reply))
    def __internalStateReadFinished(self, reply: QModbusReply) ->None:
        reply.deleteLater()
        if reply.error() != QModbusDevice.Error.NoError:
            self.__internalStateReadError(f'[Modbus protocol error]: [{reply.errorString()}][{reply.error()}]')
            return

        result = reply.result()
        if result.valueCount() != len(self.__data_buffer):
            self.__internalStateReadError(f'[Read value error]: Invalid count of reply registers: [{result.valueCount()}]:[{len(self.__value)}]')
            return

        self.__data_buffer = reply.result().values()
        self.valueChanged.emit()
    def __internalStateReadError(self, error: str) ->None:
        print('[HoldingRegisterArray][Read]', error)
        self.__data_buffer = [None for _ in self.__data_buffer]
        self.valueChanged.emit()

class HoldingRegister(AbstractReadWriteModel[int]):
    def __init__(self, origin: HoldingRegisterArray, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: HoldingRegisterArray = origin
        self.__index: int = index
        self.__origin.valueChanged.connect(lambda: self.changed.emit(self.read()))

    def read(self) ->int:
        return self.__origin.read(self.__index)
    def write(self, value: int) ->None:
        # modbus принимает только положительные числа
        # todo: Сделать в конфиге сдвиг чтобы получился положительный диаппазон (если [-150,150] то +150 -> [0,300]), 
        #       а в прошивке сделать обратный сдвиг (-150)
        if value < 0:
            value = value + 65536 # 2**16
        self.__origin.write(self.__index, value)
#==========================================================

class DiscreteInputRegisterArray(QObject):
    valueChanged: Signal = Signal()
    def __init__(self, connection: QModbusClient, server: int, register_start: int, register_count: int, timeout: int = 50, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.__connection: QModbusClient = connection
        self.__server: int = server
        self.__register_start: int = register_start
        self.__register_count: int = register_count

        self.__data_buffer: List[bool] = [None for _ in range(self.__register_count)]
        self.startTimer(timeout, Qt.TimerType.PreciseTimer)
        self.__internalStateReadRequest()

    def count(self) ->int:
        return len(self.__data_buffer)
    def read(self, index: int) ->bool:
        return self.__data_buffer[index - self.__register_start]
    def timerEvent(self, event) ->None:
        super().timerEvent(event)
        self.__internalStateReadRequest()
    def __internalStateReadRequest(self) ->None:
        read_request = QModbusDataUnit(QModbusDataUnit.RegisterType.DiscreteInputs, self.__register_start, len(self.__data_buffer))
        reply: QModbusReply = self.__connection.sendReadRequest(read_request, self.__server)
        if reply is None:
            self.__internalStateReadError('[Modbus protocol error]: [Invalid request]')
        elif reply.isFinished():
            reply.deleteLater()
            self.__internalStateReadError('[Modbus protocol error]: [Make broadcast request]')
        else:
            reply.finished.connect(lambda: self.__internalStateReadFinished(reply))
    def __internalStateReadFinished(self, reply: QModbusReply) ->None:
        reply.deleteLater()
        if reply.error() != QModbusDevice.Error.NoError:
            self.__internalStateReadError(f'[Modbus protocol error]: [{reply.errorString()}][{reply.error()}]')
            return

        result = reply.result()
        if result.valueCount() != len(self.__data_buffer):
            self.__internalStateReadError(f'[Read value error]: Invalid count of reply registers: [{result.valueCount()}]:[{len(self.__value)}]')
            return

        self.__data_buffer = reply.result().values()
        # print(self.__data_buffer)
        self.valueChanged.emit()
    def __internalStateReadError(self, error: str) ->None:
        print('[DiscreteInputRegisterArray]', error)
        print(traceback.print_stack())
        self.__data_buffer = [None for _ in self.__data_buffer]
        self.valueChanged.emit()

class DiscreteInputRegister(AbstractReadModel[bool]):
    def __init__(self, origin: DiscreteInputRegisterArray, index: int, parent: QObject):
        super().__init__(parent)
        self.__origin: DiscreteInputRegisterArray = origin
        self.__index: int = index
        self.__origin.valueChanged.connect(self.valueChanged)

    def read(self) ->bool:
        return self.__origin.read(self.__index)