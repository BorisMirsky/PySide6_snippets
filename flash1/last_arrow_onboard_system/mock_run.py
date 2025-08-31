# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget
from PySide6.QtWidgets import QApplication
from PySide6.QtWidgets import QVBoxLayout
from PySide6.QtWidgets import QPushButton
from PySide6.QtWidgets import QLineEdit
from typing import Optional, List
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
from presentation.utils.interpolation.Units import ReadInterpolationUnit
from presentation.utils.interpolation.Strategies import LinearInterpolationStrategy
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
    # sensors, controls = create_sensors_and_controls(config)
    # units = SerialPortUnitProvider(config)
    # units = MockUnitProvider(sensors, controls)
    units = MockUnitProvider(config)
    # units.event_dispatcher().traced_event_received.connect(lambda delay: print(f'Event elapsed time: {delay} s'))

    rfid_tag_scanner = MockRfidScanner(app)
    rfid_tag_scanner: RfidTagRssiFilterScanner = create_rfid_scaner(configuration=config)  
    # rfid_tag_scanner.tagReceived.connect(print)    
    
    applicationStateMachine = ApplicationStateMachine(config, units, rfid_tag_scanner, app)
    applicationView = ApplicationView(applicationStateMachine)
    applicationStateMachine.start()
    #applicationView.setWindowTitle("ПАК Стрела")
    applicationView.show()
    #applicationView.showFullScreen()
    
    # send_tag_view = SendMockRfidTagWindow(parent=None)
    # send_tag_view.tagReceived.connect(lambda tag: rfid_tag_scanner.sendRfidTag(tag.title.encode('utf-8')))
    # send_tag_view.show()

    sys.exit(app.exec())

#===========================================================================
