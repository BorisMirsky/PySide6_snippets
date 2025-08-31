# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QTranslator
from PySide6.QtCore import QIODevice
from PySide6.QtCore import QThread
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QObject
from PySide6.QtCore import QPointF
from PySide6.QtCore import QPoint
from PySide6.QtCore import QEvent
from PySide6.QtCore import QTimer
from PySide6.QtCore import QUuid
from PySide6.QtCore import Property
from PySide6.QtCore import Signal
from PySide6.QtCore import Slot
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QGridLayout, QWidget
from PySide6.QtWidgets import QApplication

from typing import *

import random
import pandas
import numpy
import time
import math
import json

#from operating.states.idle.ApplicationIdleState import ApplicationIdleState
#from operating.states.measuring.MeasuringApplicationState import MeasuringApplicationState
#from operating.states.lining.LiningApplicationState import LiningApplicationState
#from operating.states.quit.ExitApplicationState import ExitApplicationState
#from presentation.gui.common.MainApplicationWindow import MainApplicationWindow
#from presentation.gui.common.viewes.TableDataChartsView import TableDataChartsView
#from presentation.gui.common.viewes.InformationPanel import InformationPanel
#from presentation.gui.lining.LiningView import LiningView
from functools import partial
import numpy
from domain.rw_models.AbstractModels import *
from domain.rw_models.MockModels import SinMockModel, IntMockModel, MockReadWriteModel
from domain.rw_models.DistanceTravelledProvider import TickCounterMockProvider, TickCounterProvider, DistanceTravelledProvider
from domain.rw_models.MockModels import MockReadWriteModel, AbstractReadModel
# from domain.qt_models.DataframeTableModel import DynamicDataframeTableModel
from domain.dto.Travelling import Vector
from domain.interpolation.RwModels import ReadInterpolationModel, ReadWriteInterpolationModel
from domain.interpolation.Strategies import LinearInterpolationStrategy
from operating.states.ApplicationStateMachine import ApplicationStateMachine
from presentation.gui.MainApplicationWindow import ApplicationView
from domain.markers.rfid_scanners.MockRfidScanner import MockRfidScanner

def create_sensors_and_controls(configuration: dict) ->(dict, dict):
    sensors = dict()
    controls = dict()

    for sensor_name, sensor_params in configuration['models']['sensors'].items():
        if sensor_name == 'tick_counter':
            sensors[sensor_name] = TickCounterMockProvider(25, QApplication.instance())
        elif sensor_name == 'discrete_signals':
            origin = IntMockModel(0, 2**32, QApplication.instance())
            sensors[sensor_name] = origin
        else:
            origin = SinMockModel(5, random.random() * 5, 0.1, QApplication.instance())
            # projection = ReadInterpolationModel(origin, LinearInterpolationStrategy(
            #     (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
            #     (sensor_params['value_range']['min'], sensor_params['value_range']['max'])
            #     ), origin)
            # sensors[sensor_name] = projection
            sensors[sensor_name] = origin

    origin = MockReadWriteModel(QApplication.instance())
    modbus_to_milliamperes = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy((205, 819), (-15, 15)), origin)
    milliamperes_to_millimeters = ReadWriteInterpolationModel(modbus_to_milliamperes, LinearInterpolationStrategy((-15, 15), (-100, 100)), origin)
    controls['lining'] = milliamperes_to_millimeters

    origin = MockReadWriteModel(QApplication.instance())
    modbus_to_milliamperes = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy((205, 819), (-15, 15)), origin)
    milliamperes_to_millimeters = ReadWriteInterpolationModel(modbus_to_milliamperes, LinearInterpolationStrategy((-15, 15), (-100, 100)), origin)
    controls['lifting_left'] = milliamperes_to_millimeters

    origin = MockReadWriteModel(QApplication.instance())
    modbus_to_milliamperes = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy((205, 819), (-15, 15)), origin)
    milliamperes_to_millimeters = ReadWriteInterpolationModel(modbus_to_milliamperes, LinearInterpolationStrategy((-15, 15), (-100, 100)), origin)
    controls['lifting_right'] = milliamperes_to_millimeters


    for control_name, control_params in configuration['models']['controls'].items():
        origin = MockReadWriteModel(QApplication.instance())
        # projection = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy((1024, 0), (-15, 15)), origin)
        projection = ReadWriteInterpolationModel(origin, LinearInterpolationStrategy(
            (control_params['projection_range']['min'], control_params['projection_range']['max']),
            (control_params['value_range']['min'], control_params['value_range']['max'])
            ), origin)
        controls[control_name] = projection


#    connection = QModbusRtuSerialClient(QApplication.instance())
#    connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialPortNameParameter, configuration['models']['connection']['port']);
#    connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialBaudRateParameter, configuration['models']['connection']['baud_rate']);
#    connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialParityParameter, QSerialPort.Parity.NoParity);
#    connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialDataBitsParameter, 8);
#    connection.setConnectionParameter(QModbusDevice.ConnectionParameter.SerialStopBitsParameter, 1);
#    connection.setTimeout(1000)#ms
#    connection.setNumberOfRetries(3)
#    if not connection.connectDevice():
#        raise Exception(f'Modbus connection error: {connection.errorString()}')

#    server_id = configuration['models']['connection']['server_id']
#    enable_register = HoldingRegister(connection, server_id, 0, QApplication.instance())
#    enable_register.write(1)
#    speed_register = HoldingRegister(connection, server_id, 1, QApplication.instance())
#    speed_register.write(40)

#    models['distance_sensor'] = PositionMock(0.05, QApplication.instance())
#    for sensor_name, sensor_params in configuration['models']['sensors'].items():
#        if sensor_name == 'tick_counter':
#            register = HoldingRegister(connection, server_id, sensor_params['register_id'], QApplication.instance())
#            sensors[sensor_name] = TickCounterProvider(register, register)
#        else:
#            register = HoldingRegister(connection, server_id, sensor_params['register_id'], QApplication.instance())
#            projection = FloatValueReadExpander(register,
#                (sensor_params['projection_range']['min'], sensor_params['projection_range']['max']),
#                (sensor_params['value_range']['min'], sensor_params['value_range']['max']), register)
#            sensors[sensor_name] = projection
#    for control_name, control_params in configuration['models']['controls'].items():
#        register = HoldingRegister(connection, server_id, control_params['register_id'], QApplication.instance())
#        projection = FloatValueReadWriteExpander(register,
#            (control_params['projection_range']['min'], control_params['projection_range']['max']),
#            (control_params['value_range']['min'], control_params['value_range']['max']), register)
#        controls[control_name] = projection

    return (sensors, controls)


#===========================================================================

#===========================================================================
from domain.markers.rfid_scanners.UhfSlr1104RfidScanner import UhfSlr1104RfidScanner
if __name__ == '__main__':
    app = QApplication(sys.argv)

    translator = QTranslator(app)
    translator.load('./resources/translations/ru.qm')
    app.installTranslator(translator)


    rfid_tag_scanner = UhfSlr1104RfidScanner('', 10001, app)
    rfid_tag_scanner.tagReceived.connect(print)
    rfid_tag_scanner.start()
    def close_rfid_tag_scanner_thread():
        rfid_tag_scanner.requestInterruption()
        rfid_tag_scanner.wait()
    app.aboutToQuit.connect(close_rfid_tag_scanner_thread)

    config = json.load(open('./resources/config.json'))
    sensors, controls = create_sensors_and_controls(config)
    print('Sensors:', sensors)
    print('Controls:', controls)

    # rfid_tag_scanner = MockRfidScanner(app)

    applicationStateMachine = ApplicationStateMachine(config, sensors, controls, rfid_tag_scanner, app)
    applicationView = ApplicationView(applicationStateMachine)
    applicationStateMachine.start()
    applicationView.show()
    sys.exit(app.exec())

#===========================================================================













#if __name__ == '__main__':
#    from domain.rw_models.interpolation.AbstractStrategy import LinearInterpolationStrategy, FunctionInterpolationStrategy, ForwardInterpolationStrategyTableModel, BackwardInterpolationStrategyTableModel
#    app = QApplication([])


##    xInterpolator = eval("lambda x: x**2", {'__builtins__': { 'math': math, 'numpy': numpy } })
##    yInterpolator = eval("lambda x: x", globals=None, locals=None)


##    exec('''def xInterpolator(x: float) ->float:
##        if abs(x) <= 1:
##            return math.pow(x, 3)
##        elif x < 0:
##            return 2 * x + 1
##        else:
##            return 2 * x - 1
##    ''')
##    exec('''def yInterpolator(y: float) ->float:
##        if abs(y) <= 1:
##            return math.cbrt(y)
##        elif y < 0:
##            return (y - 1) / 2
##        else:
##            return (y + 1) / 2
##    ''')


#    exec('''def xInterpolator(y: float) ->float:
#        return math.cbrt(y)
#    ''')
#    exec('''def yInterpolator(x: float) ->float:
#        return math.pow(x, 3)
#    ''')

#    #interpolation = LinearInterpolationStrategy((0, 1000), (-10, 10))
#    interpolation = FunctionInterpolationStrategy(xInterpolator, yInterpolator)
#    model_1 = ForwardInterpolationStrategyTableModel(interpolation, (-8000, 8000), 1000)
#    series_1 = QLineSeries()
#    mapper_1 = QVXYModelMapper()
#    mapper_1.setSeries(series_1)
#    mapper_1.setXColumn(0)
#    mapper_1.setYColumn(1)
#    mapper_1.setModel(model_1)

#    chart_1 = QChart()
#    chart_1.addSeries(series_1)
#    chart_1.createDefaultAxes()

#    view_1 = QChartView(chart_1)
#    view_1.resize(640, 480)
#    view_1.show()

#    model_2 = BackwardInterpolationStrategyTableModel(interpolation, (-20, 20), 1000)
#    series_2 = QLineSeries()
#    mapper_2 = QVXYModelMapper()
#    mapper_2.setSeries(series_2)
#    mapper_2.setXColumn(0)
#    mapper_2.setYColumn(1)
#    mapper_2.setModel(model_2)

#    chart_2 = QChart()
#    chart_2.addSeries(series_2)
#    chart_2.createDefaultAxes()

#    view_2 = QChartView(chart_2)
#    view_2.resize(640, 480)
#    view_2.show()
#    sys.exit(app.exec())

#======================================================================

#if __name__ == '__main__':
#    app = QApplication([])
#    config = json.load(open('./resources/config.json'))
#    rw_models = create_sensors_and_controls(config)
#    meauserments_model = DataframeTableModel(config, app)


#    insertDataTimer = QTimer()
#    def createNewMeauserment():
#        record = { 'position': rw_models['position'].read() }
#        for sensor_name, sensor in rw_models['sensors'].items():
#            record[sensor_name] = sensor.read()

#        meauserments_model.appendDataRow(pandas.DataFrame([record.values()], columns=record.keys()))
#    insertDataTimer.timeout.connect(createNewMeauserment)
#    insertDataTimer.start(150)


#    stateMachine = QStateMachine(QState.ChildMode.ExclusiveStates, app)
#    idle = IdleApplicationState(stateMachine)
#    measuring = MeasuringApplicationState(meauserments_model, stateMachine)
#    lining = LiningApplicationState(stateMachine)
#    exit = ExitApplicationState(config, stateMachine)
#    stateMachine.setInitialState(idle)

#    idle.addTransition(idle.measuringActivated, measuring)
#    idle.addTransition(idle.liningActivated, lining)
#    idle.addTransition(idle.quitActivated, exit)
#    measuring.addTransition(measuring.measuringFinished, idle)
#    lining.addTransition(lining.liningFinished, idle)


#    idle.entered.connect(meauserments_model.reset)
#    measuring.entered.connect(meauserments_model.reset)
#    lining.entered.connect(meauserments_model.reset)
#    exit.entered.connect(meauserments_model.reset)
#    window = MainApplicationWindow(config, rw_models, meauserments_model, idle, measuring, lining, exit)
#    window.resize(640, 480)
#    window.show()
#    stateMachine.start()
#    sys.exit(app.exec())









#======================================================================

#if __name__ == '__main__':
#    def print_example(previous, current):
#        print(f'[{previous}] => [{current}] = [{current - previous}]')


#    print_example(0, 1)
#    print_example(1, 0)
#    print_example(10, 12)
#    print_example(12, 10)
#    print_example(65530, 10)
#    print_example(10, 65530)

#    app = QApplication([])
#    raw_counter = MockReadWriteModel[int]()
#    raw_counter.write(13)
#    owr_counter = TickCounterProvider(raw_counter, raw_counter.read())
#    distance_calculator = DistanceTravelledProvider(owr_counter, 42, 0.475)

#    minus_button = QPushButton('- 1')
#    plus_button = QPushButton('+ 1')
#    raw_label = QLabel(str(raw_counter.read()))
#    owr_label = QLabel(str(owr_counter.read()))
#    distance_label = QLabel(str(distance_calculator.read()))

#    minus_button.clicked.connect(lambda: raw_counter.write((raw_counter.read() - 1) % 65536))
#    plus_button.clicked.connect(lambda: raw_counter.write((raw_counter.read() + 1) % 65536))
#    raw_counter.valueChanged.connect(lambda: raw_label.setNum(raw_counter.read()))
#    owr_counter.valueChanged.connect(lambda: owr_label.setNum(owr_counter.read()))
#    distance_calculator.valueChanged.connect(lambda: distance_label.setNum(distance_calculator.read()))



#    window = QWidget()
#    layout = QGridLayout()
#    window.setLayout(layout)
#    layout.addWidget(raw_label, 0, 0, 1, 2)
#    layout.addWidget(owr_label, 0, 2, 1, 2)
#    layout.addWidget(distance_label, 0, 4, 1, 2)
#    layout.addWidget(minus_button, 1, 0, 1, 3)
#    layout.addWidget(plus_button, 1, 3, 1, 3)
#    window.show()
#    sys.exit(app.exec())
