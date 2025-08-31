from domain.units.AbstractUnit import AbstractReadUnit, AbstractReadWriteUnit
from domain.units.AbstractUnitProvider import AbstractUnitProvider
from PySide6.QtSerialBus import QSerialPort
from typing import Dict

class ModbusUnitProvider(AbstractUnitProvider):
    def __init__(self, config: dict, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__controls: Dict[str, AbstractReadWriteUnit] = {}
        self.__sensors: Dict[str, AbstractReadUnit] = {}

        # ============================================================

        self.__connection = QModbusRtuSerialClient(QApplication.instance())
        self.__connection.stateChanged.connect(self.__connection_state_changed)
        self.__connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialPortNameParameter, configuration['models']['connection']['port'])
        self.__connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialBaudRateParameter, configuration['models']['connection']['baud_rate'])
        self.__connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialParityParameter, QSerialPort.Parity.NoParity)
        self.__connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialDataBitsParameter, 8)
        self.__connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialStopBitsParameter, 1)
        self.__connection.setTimeout(1000)#ms
        self.__connection.setNumberOfRetries(3)
        self.__try_modbus_reconnect()

        # ============================================================

        server_id = configuration['models']['connection']['server_id']
        controls_registers = HoldingRegisterArray(connection, server_id, 0, 11, parent = QApplication.instance())
        sensor_registers = InputRegisterArray(connection, server_id, 12, 17, parent = QApplication.instance())

        enable_register = HoldingRegister(controls_registers, 0, QApplication.instance())
        enable_register.write(1)
        speed_register = HoldingRegister(controls_registers, 1, QApplication.instance())
        speed_register.write(40)

        # ============================================================

    def __connection_state_changed(self) ->None:
        if self.__connection.state() == QModbusDevice.State.UnconnectedState:
            self.__try_modbus_reconnect()

    def __try_modbus_reconnect(self) ->None:
        connection.disconnectDevice()
        if not connection.connectDevice():
            raise Exception(f'Modbus connection error: {connection.errorString()}')

    def get_all_read_only_units(self) ->Dict[str, AbstractReadUnit]:
        return self.__controls
    def get_all_readwrite_units(self) ->Dict[str, AbstractReadWriteUnit]:
        return self.__sensors



        # server_id = configuration['models']['connection']['server_id']
        # controls_registers = HoldingRegisterArray(connection, server_id, 0, 11, parent = QApplication.instance())
        # sensor_registers = InputRegisterArray(connection, server_id, 12, 17, parent = QApplication.instance())

        # enable_register = HoldingRegister(controls_registers, 0, QApplication.instance())
        # enable_register.write(1)
        # speed_register = HoldingRegister(controls_registers, 1, QApplication.instance())
        # speed_register.write(40)

        # # Создание датчиков
        # for sensor_name, sensor_params in configuration['models']['sensors'].items():
            
        #     if sensor_name == 'tick_counter':     
        #         register = InputRegister(sensor_registers, sensor_params['register_id'], QApplication.instance())       
        #         # sensors[sensor_name] = TickCounterProvider(register, register)
        #         sensors[sensor_name] = TickCounterProviderEx(register, sensor_params['inverse'], register)
        #     elif sensor_name == 'discrete_signals':
        #         register = InputRegister(sensor_registers, sensor_params['register_id'], QApplication.instance())
        #         sensors[sensor_name] = register 
        #     elif sensor_name == 'satellite':
        #         if not sensor_params.get('disabled', False):
        #             register = SignedInputRegister(sensor_registers, sensor_params['register_id'], QApplication.instance())
        #             projection = ReadInterpolationModel(register, LinearInterpolationStrategy(
        #                 (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
        #                 (sensor_params['value_range']['min'], sensor_params['value_range']['max'])
        #                 ), parent=register)
        #         else:
        #             projection = MemoryBufferModel(0.0)

        #         sensors[sensor_name] = projection
        #     else:            
        #         register = SignedInputRegister(sensor_registers, sensor_params['register_id'], parent=QApplication.instance())
        #         projection = ReadInterpolationModel(register, LinearInterpolationStrategy(
        #             (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
        #             (sensor_params['value_range']['min'], sensor_params['value_range']['max'])     ), 
        #             inverse=sensor_params.get('inverse', False), 
        #             parent=register)
        #         sensors[sensor_name] = projection

        #     # Создание датчиков
        #     for control_name, control_params in configuration['models']['controls'].items():
        #         controls[control_name] = create_servo_control(params=control_params, controls_registers=controls_registers)
