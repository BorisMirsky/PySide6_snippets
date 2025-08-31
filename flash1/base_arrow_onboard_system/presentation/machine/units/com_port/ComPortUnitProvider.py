
import functools
from typing import Optional, Dict
from PySide6.QtCore import QObject, QIODevice
from PySide6.QtWidgets import QApplication
from PySide6.QtSerialPort import QSerialPort

from domain.units.MemoryBufferUnit import MemoryBufferUnit
from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from presentation.utils.interpolation.Units import ReadInterpolationUnit, ReadWriteInterpolationUnit
from presentation.utils.interpolation.Strategies import LinearInterpolationStrategy, FunctionInterpolationStrategy
from presentation.utils.interpolation.ServoStrategies import servo_piecewise_linear_interpolation
from presentation.machine.units.DistanceTravelledUnits import TickCounterProvider2
from presentation.machine.units.com_port.ComPortUnits import ComPortController, ComPortControllerStreamOptions, ComPortReadUnit, ComPortReadWriteUnit, SignedComPortReadUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from presentation.machine.units.DistanceTravelledUnits import DistanceTravelledProvider
from domain.dto.Travelling import MovingDirection
from presentation.machine.units.DiscreteSignalsUnit import DiscreteSignalsUnit
from domain.dto.DiscreteSignals import DiscreteSignalsContainer
from presentation.machine.units.UIEventDelayUnit import TraceEventDispatcherQueueReceiver
from presentation.machine.units.StrelographUnit import StrelographUnit


class SerialPortUnitProvider(AbstractUnitProvider):
    @staticmethod
    def nop(v):
        return v

    @staticmethod
    def calculate_crc_function(header: bytes, data: bytes) ->bytes:
        return bytes([((256 - (sum(bytes([header[1]]) + data) & 0xFF)) & 0xFF)])
    
    def __init__(self, configuration: dict, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)        
        self.__controls: Dict[str, AbstractReadWriteUnit] = {}
        self.__sensors: Dict[str, AbstractReadUnit] = {}

        # ============================================================
        
        self.__connection = QSerialPort(configuration['models']['connection']['port'])        
        self.__connection.setBaudRate(configuration['models']['connection']['baud_rate'])
        if not self.__connection.open(QIODevice.OpenMode.ReadWrite):
            raise Exception(f"Unavailable com port for connection '{configuration['models']['connection']['port']}'")
        
        poll_timer = configuration['models']['connection'].get('poll_timer', 50)
        receive_count = configuration['models']['connection']['receive_items_count']
        send_count = configuration['models']['connection']['send_items_count']
        self.__controller = ComPortController(
            stream = self.__connection,
            receive_options = ComPortControllerStreamOptions(bytes([0x77, 0x55]), receive_count, SerialPortUnitProvider.calculate_crc_function),
            send_options = ComPortControllerStreamOptions(bytes([0x77, 0xE4]), send_count, SerialPortUnitProvider.calculate_crc_function),
            sync_state_timeout = poll_timer)

        # Разрешение/запрет обмена
        enable_register = ComPortReadWriteUnit(self.__controller, 0, QApplication.instance())
        enable_register.write(0)
        self.__controls['enable_register'] = enable_register

        # Признак того что контроллер обменивается пакетами
        self.__controller_heartbeat = ComPortReadUnit(self.__controller, 0, QApplication.instance()) 
        # self.__controller_heartbeat.valueChanged.connect(lambda: print(f'controller_heartbeat: {self.__controller_heartbeat.read()}'))
        # self.__controller.valueChanged.connect(lambda: print(f'controller_value_changed'))

        # Создание датчиков
        for sensor_name, sensor_params in configuration['models']['sensors'].items():            
            if sensor_name == 'tick_counter':                     
                register = ComPortReadUnit(self.__controller, sensor_params['register_id'], QApplication.instance())                                       
                self.__sensors[sensor_name] = TickCounterProvider2(register, sensor_params['inverse'], register)
            elif sensor_name == 'discrete_signals':
                register = ComPortReadUnit(self.__controller, sensor_params['register_id'], QApplication.instance())
                self.__sensors[sensor_name] = register 
            elif sensor_name == 'satellite':
                if not sensor_params.get('disabled', False):
                    register = SignedComPortReadUnit(self.__controller, sensor_params['register_id'], QApplication.instance())
                    projection = ReadInterpolationUnit(register, LinearInterpolationStrategy(
                        (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
                        (sensor_params['value_range']['min'], sensor_params['value_range']['max'])
                        ), parent=register)
                else:
                    projection = MemoryBufferUnit()
                    projection.write(0)
                self.__sensors[sensor_name] = projection
            elif sensor_name == 'strelograph_work':
                origin = SignedComPortReadUnit(self.__controller, sensor_params['register_id'], parent=self)
                strelograph_unit = StrelographUnit(origin=origin, params=sensor_params, parent=origin)
                self.__sensors[sensor_name] = strelograph_unit
            else:            
                register = SignedComPortReadUnit(self.__controller, sensor_params['register_id'], parent=QApplication.instance())
                projection = ReadInterpolationUnit(register, LinearInterpolationStrategy(
                    (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
                    (sensor_params['value_range']['min'], sensor_params['value_range']['max'])     ), 
                    inverse=sensor_params.get('inverse', False), 
                    parent=register)
                self.__sensors[sensor_name] = projection
        
        # Создание управляющих регистров
        for control_name, control_params in configuration['models']['controls'].items():
            self.__controls[control_name] = self.__create_servo_control(params=control_params)

        # self.__position_unit = DistanceTravelledProvider(MovingDirection.Forward, self.__sensors['tick_counter'], configuration['machine_parameters']['ticks_number'] / configuration['machine_parameters']['ticks_distance'])
        self.__ticks_per_meter = configuration['machine_parameters']['ticks_number'] / configuration['machine_parameters']['ticks_distance']
        self.__discrete_signals_container: AbstractReadUnit[DiscreteSignalsContainer] = DiscreteSignalsUnit(self.__sensors['discrete_signals'])
        self.__event_dispatcher = TraceEventDispatcherQueueReceiver(1000)

    def close(self) -> None:
        if self.__connection is not None:
            self.__connection.close()

    def controller(self) ->ComPortController:
        return self.__controller
    
    # def position_unit(self) ->AbstractReadUnit[float]:
    #     return self.__position_unit
    
    def create_position_unit(self, direction: MovingDirection) ->AbstractReadWriteUnit[float]:
        return DistanceTravelledProvider(direction, self.__sensors['tick_counter'], self.__ticks_per_meter)
    
    def discrete_signals_container(self) ->AbstractReadUnit[float]:
        return self.__discrete_signals_container
    
    def get_all_read_only_units(self) ->Dict[str, AbstractReadUnit]:
        return self.__sensors
    def get_all_readwrite_units(self) ->Dict[str, AbstractReadWriteUnit]:
        return self.__controls

    def controls(self) ->Dict[str, AbstractReadWriteUnit]:
        return self.__controls
    def sensors(self) ->Dict[str, AbstractReadUnit]:
        return self.__sensors
    
    @property
    def controller_communication_allowed(self) -> bool:
        return bool(self.__controls['enable_register'].read())

    @controller_communication_allowed.setter
    def controller_communication_allowed(self, value: bool):
        self.__controls['enable_register'].write(int(value))
    
    def __create_servo_control(self, params: dict) -> ReadWriteInterpolationUnit: 
        """
        Для сервовентилей реализовано два типа интерполяции: линейная и кусочно-линейная.
        По умолчанию используется линейная интерполяци если не задано иное.
        """
        func_type = params.get('interpolation_type', 'linear')    
        origin = ComPortReadWriteUnit(self.__controller, params['register_id'], QApplication.instance())
        origin_range = (params['projection_range']['min'], params['projection_range']['max'])
        value_range = (params['value_range']['min'], params['value_range']['max'])

        if func_type == 'piecewise_linear': 
            servo_func = functools.partial(
                            servo_piecewise_linear_interpolation, 
                            start_value=params['projection_range'].get('start_value', 0), 
                            zero_value=params['projection_range']['zero'] , 
                            zero_range=params['value_range']['zero_range'] , 
                            modbus_range=origin_range, 
                            value_range=value_range)
            strategy = FunctionInterpolationStrategy(SerialPortUnitProvider.nop, servo_func)
        else:        
            strategy =  LinearInterpolationStrategy(origin_range, value_range)
            
        return ReadWriteInterpolationUnit(origin=origin, interpolation=strategy, inverse=False, parent=origin)
        
    def event_dispatcher(self):
        return self.__event_dispatcher