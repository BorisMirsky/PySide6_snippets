# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QLineEdit
from typing import Optional
import random
import json
from PySide6.QtCore import QTranslator
from presentation.machine.markers.rfid_scanners.RfidTagRssiFilterScanner import RfidTagRssiFilterScanner
from presentation.machine.markers.rfid_scanners.UhfSlr1104RfidScanner import UhfSlr1104RfidScanner
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
#from presentation.machine.units.UIEventDelayUnit import TraceEventDispatcherQueueReceiver
# from qt_material import apply_stylesheet



from presentation.machine.markers.rfid_scanners.MockRfidScanner import MockRfidScanner
from domain.dto.Markers import RailwayMarker, RailwayMarkerLocation, RailwayMarkerType
# from domain.interpolation.ServoStrategies import servo_lining_interpolation, servo_left_interpolation, servo_right_interpolation
from presentation.machine.units.DistanceTravelledUnits import TickCounterProvider, TickCounterProvider2
from presentation.machine.units.mock.MockUnits import IntMockUnit, SinMockUnit, ConstantValueMockUnit, TickCounterMockProvider
from presentation.machine.units.mock.MockUnitProvider import MockUnitProvider
from presentation.machine.units.DistanceTravelledUnits import DistanceTravelledProvider
from domain.units.MemoryBufferUnit import MemoryBufferUnit
from domain.dto.Travelling import MovingDirection
from operating.states.ApplicationStateMachine import ApplicationStateMachine
from presentation.ui.gui.MainApplicationWindow import ApplicationView
from presentation.machine.units.StrelographUnit import StrelographUnit

#===========================================================================
def create_rfid_scaner(configuration: dict) -> RfidTagRssiFilterScanner:
    rfid_scanner_config = configuration.get('rfid_scanner', {})
    scanners: List[AbstractRfidScanner] = []
    for scanner_config in rfid_scanner_config.get('scanners', []):
        match (scanner_type := scanner_config.get('model', None)):
            case 'ThingmagicM6ERfidScanner':
                from presentation.machine.markers.rfid_scanners.ThingmagicM6ERfidScanner import ThingmagicM6ERfidScanner
                scanners.append(ThingmagicM6ERfidScanner(
                    host = scanner_config.get('host'),
                    antennas = scanner_config.get('antennas'),
                    protocol = scanner_config.get('protocol'),
                    region = scanner_config.get('region'),
                    parent = QApplication.instance()
                ))
                break
            case 'UhfSlr1104RfidScanner':
                scanners.append(UhfSlr1104RfidScanner(
                    host = scanner_config.get('host'),
                    port = scanner_config.get('port'),
                    parent = QApplication.instance()
                ))
                break
            case _:
                print(f'Error: undefined model of scanner: {scanner_type}')

    return RfidTagRssiFilterScanner(scanners = scanners,
        check_timeout_ms = rfid_scanner_config.get('check_timeout_ms', 50),
        expire_timeout_ms = rfid_scanner_config.get('expire_timeout_ms', 1000),
        parent = QApplication.instance()
    )

#===========================================================================

def create_sensors_and_controls(configuration: dict) -> tuple[dict, dict]:
    sensors = dict()
    controls = dict()

    for sensor_name, sensor_params in configuration['models']['sensors'].items():
        if sensor_name == 'tick_counter':
            register = TickCounterMockProvider(25, ticks_direction=MovingDirection.Backward, parent=QApplication.instance())
            sensors[sensor_name] = TickCounterProvider(register, sensor_params['inverse'], register)
            #sensors[sensor_name] = ConstantValueMockUnit(value=100, parent=QApplication.instance())
        elif sensor_name == 'discrete_signals':
            # sensors[sensor_name] = ConstantValueMockUnit(value=0, parent=QApplication.instance())
            sensors[sensor_name] = IntMockUnit(bottom=0, top=117, parent=QApplication.instance())
        elif sensor_name == 'sagging_left':
            sensors[sensor_name] = ConstantValueMockUnit(value=-10, parent=QApplication.instance())
            # sensors[sensor_name] = IntMockUnit(bottom=-10, top=18, parent=QApplication.instance())
        elif sensor_name == 'sagging_right':
            # sensors[sensor_name] = IntMockUnit(bottom=-10, top=2, parent=QApplication.instance())
            sensors[sensor_name] = ConstantValueMockUnit(value=-10, parent=QApplication.instance())
        elif sensor_name == 'strelograph_work':
            mock_unit = ConstantValueMockUnit(value=357, parent=QApplication.instance())
            # sensors[sensor_name] = IntMockUnit(bottom=-12, top=17, parent=QApplication.instance())
            sensors[sensor_name] = StrelographUnit(origin=mock_unit, params=sensor_params, parent=QApplication.instance())
        elif sensor_name == 'pendulum_front':
            sensors[sensor_name] = ConstantValueMockUnit(value=20, parent=QApplication.instance())
            # sensors[sensor_name] = IntMockUnit(bottom=0, top=15, parent=QApplication.instance())
        elif sensor_name == 'pendulum_control':
            sensors[sensor_name] = ConstantValueMockUnit(value=-2, parent=QApplication.instance())
            # sensors[sensor_name] = IntMockUnit(bottom=0, top=10, parent=QApplication.instance())
        elif sensor_name == 'pendulum_work':
            sensors[sensor_name] = ConstantValueMockUnit(value=30, parent=QApplication.instance())
            # sensors[sensor_name] = IntMockUnit(bottom=0, top=10, parent=QApplication.instance())
        elif sensor_name == 'satellite':
            sensors[sensor_name] = ConstantValueMockUnit(value=0)
            # sensors[sensor_name] = IntMockUnit(bottom=0, top=2, parent=QApplication.instance())
        else:
            sensors[sensor_name] = SinMockUnit(2, random.uniform(0.1, 0.2), 0.1)

    controls['enable_register'] = MemoryBufferUnit(1)

    for control_name, control_params in configuration['models']['controls'].items():
        controls[control_name] = MemoryBufferUnit(0.0)

    return (sensors, controls)


#===========================================================================

#===========================================================================

class SendMockRfidTagWindow(QWidget):
    tagReceived: Signal = Signal(RailwayMarker)
    def __init__(self, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)

        self.__tag_id = QLineEdit()
        self.__push_tag = QPushButton('Send tag')

        self.__tag_id.setPlaceholderText('Rfid tag id...')
        self.__tag_id.returnPressed.connect(self.__send_tag)
        self.__push_tag.clicked.connect(self.__send_tag)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.__tag_id)
        layout.addWidget(self.__push_tag)

    def __send_tag(self) ->None:
        self.tagReceived.emit(RailwayMarker(
            title = self.__tag_id.text(),
            type = RailwayMarkerType.RfidTag,
            location = RailwayMarkerLocation.Middle
        ))
        self.__tag_id.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # disp = TraceEventDispatcherQueueReceiver(100)
    translator = QTranslator(app)
    translator.load('./resources/translations/ru.qm')
    app.installTranslator(translator)

    app.setStyleSheet(app.styleSheet() + open('./resources/style/style.qss', 'r').read())

    config = json.load(open('./resources/config.json', mode='r' , encoding='utf-8'))
    sensors, controls = create_sensors_and_controls(config)

    rfid_tag_scanner = MockRfidScanner(app)
    #rfid_tag_scanner: RfidTagRssiFilterScanner = create_rfid_scaner(configuration=config)
    rfid_tag_scanner.tagReceived.connect(print)
    send_tag_view = SendMockRfidTagWindow()
    send_tag_view.tagReceived.connect(lambda tag: rfid_tag_scanner.sendRfidTag(tag.title.encode('utf-8')))
#    send_tag_view.show()
    # units = SerialPortUnitProvider(config)
    units = MockUnitProvider(sensors, controls)
    # units.event_dispatcher().traced_event_received.connect(lambda delay: print(f'Event elapsed time: {delay} s'))
    applicationStateMachine = ApplicationStateMachine(config, units, rfid_tag_scanner, app)
    applicationView = ApplicationView(applicationStateMachine)
    applicationStateMachine.start()
    applicationView.show()
    #applicationView.showFullScreen()
    sys.exit(app.exec())

#===========================================================================
