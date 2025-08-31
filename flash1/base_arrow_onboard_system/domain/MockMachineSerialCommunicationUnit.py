
import random
import functools
from typing import Optional, Dict
from PySide6.QtCore import QObject, QTimer, QIODevice
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtSerialPort import QSerialPort

from domain.rw_models.DistanceTravelledProvider import TickCounterProviderEx
from domain.interpolation.RwModels import ReadInterpolationModel, ReadWriteInterpolationModel
from domain.rw_models.AbstractModels import AbstractReadWriteModel, AbstractReadModel, MemoryBufferModel
from domain.interpolation.Strategies import LinearInterpolationStrategy, FunctionInterpolationStrategy
from domain.interpolation.ServoStrategies import servo_piecewise_linear_interpolation
from domain.rw_models.MockModels import SinMockModel, IntMockModel, MockReadWriteModel, ConstantValueMockModel
from domain.rw_models.DistanceTravelledProvider import TickCounterMockProvider, TickCounterProvider, DistanceTravelledProvider
from domain.rw_models.MockModels import MockReadWriteModel, AbstractReadModel


def create_sensors_and_controls(configuration: dict) -> tuple[dict, dict]:
    sensors = dict()
    controls = dict()

    for sensor_name, sensor_params in configuration['models']['sensors'].items():
        if sensor_name == 'tick_counter':
            # sensors[sensor_name] = TickCounterMockProvider(25, QApplication.instance())
            sensors[sensor_name] = ConstantValueMockModel(value=0, parent=QApplication.instance())
        elif sensor_name == 'discrete_signals':            
            sensors[sensor_name] = ConstantValueMockModel(value=117, parent=QApplication.instance())
        elif sensor_name == 'sagging_left':
            sensors[sensor_name] = ConstantValueMockModel(value=-10, parent=QApplication.instance())
        elif sensor_name == 'sagging_right':
            sensors[sensor_name] = ConstantValueMockModel(value=-10, parent=QApplication.instance())
        elif sensor_name == 'strelograph_work':
            sensors[sensor_name] = ConstantValueMockModel(value=10, parent=QApplication.instance())
        elif sensor_name == 'pendulum_front':
            sensors[sensor_name] = ConstantValueMockModel(value=0, parent=QApplication.instance())
        elif sensor_name == 'pendulum_work':
            sensors[sensor_name] = ConstantValueMockModel(value=0, parent=QApplication.instance())
        elif sensor_name == 'satellite':
            sensors[sensor_name] = ConstantValueMockModel(value=0)
        else:
            origin = SinMockModel(5, random.random() * 5, 0.1, QApplication.instance())
            # projection = ReadInterpolationModel(origin, LinearInterpolationStrategy(
            #     (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
            #     (sensor_params['value_range']['min'], sensor_params['value_range']['max'])
            #     ), origin)
            # sensors[sensor_name] = projection
            sensors[sensor_name] = origin


    enable_register = MockReadWriteModel(QApplication.instance())
    enable_register.write(1)
    controls['enable_register'] = enable_register

    for control_name, control_params in configuration['models']['controls'].items():
        origin = MockReadWriteModel(QApplication.instance())
        # projection = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy((1024, 0), (-15, 15)), origin)
        projection = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy(
            (control_params['projection_range']['min'], control_params['projection_range']['max']),
            (control_params['value_range']['min'], control_params['value_range']['max'])
            ), origin)
        controls[control_name] = projection

    return (sensors, controls)


class MockMachineSerialCommunicationUnit(QObject):
    @staticmethod
    def calculate_crc_function(header: bytes, data: bytes) ->bytes:
        return bytes([((256 - (sum(bytes([header[1]]) + data) & 0xFF)) & 0xFF)])
    
    def __init__(self, configuration: dict, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__modbus_heartbeat_value = -1
        self.__strela_heartbeat_value = 0
        self.__controls: Dict[str, AbstractReadWriteModel] = {}
        self.__sensors: Dict[str, AbstractReadModel] = {}

        self.__sensors, self.__controls = create_sensors_and_controls(configuration)
        

    def controls(self) ->Dict[str, AbstractReadModel]:
        return self.__controls
    def sensors(self) ->Dict[str, AbstractReadWriteModel]:
        return self.__sensors
    
    @property
    def controller_communication_allowed(self) -> bool:
        return True

    @controller_communication_allowed.setter
    def controller_communication_allowed(self, value: bool):
        pass
    
        
def nop(v):
    return v