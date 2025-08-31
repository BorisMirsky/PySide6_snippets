# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtCore import QTranslator
from PySide6.QtWidgets import QApplication
import json
from typing import List

from operating.states.ApplicationStateMachine import ApplicationStateMachine
from presentation.ui.gui.MainApplicationWindow import ApplicationView
from presentation.machine.units.com_port.ComPortUnitProvider import SerialPortUnitProvider
from presentation.machine.units.com_port.ComPortUnitProviderAsync import SerialPortUnitProviderAsync
from presentation.machine.markers.rfid_scanners.RfidTagRssiFilterScanner import RfidTagRssiFilterScanner
# from presentation.machine.markers.rfid_scanners.ThingmagicM6ERfidScanner import ThingmagicM6ERfidScanner
from presentation.machine.markers.rfid_scanners.UhfSlr1104RfidScanner import UhfSlr1104RfidScanner
from domain.markers.AbstractRfidScanner import AbstractRfidScanner


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


if __name__ == '__main__':
    # from domain.rfid.MockRfidScanner import MockRfidScanner    
    app = QApplication(sys.argv)

    # disp = TraceEventDispatcherQueueReceiver(100)

    translator = QTranslator(app)
    translator.load('./resources/translations/ru.qm')
    app.installTranslator(translator)
    
    app.setStyleSheet(app.styleSheet() + open('./resources/style/style.qss', 'r').read())
    
    config = json.load(open('./resources/config.json', mode='r', encoding='utf-8'))
    rfid_tag_scanner: RfidTagRssiFilterScanner = create_rfid_scaner(configuration=config)    

    applicationStateMachine = ApplicationStateMachine(
                                    config=config, 
                                    units=SerialPortUnitProviderAsync(config), 
                                    rfid_tag_scanner=rfid_tag_scanner, 
                                    parent=app)
    
    applicationStateMachine.idle.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.idle.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.programTaskCalculation.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.programTaskCalculation.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.maintenance.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.maintenance.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.measuring.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.measuring.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.lining.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.lining.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.quit.entered.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationStateMachine.quit.exited.connect(rfid_tag_scanner.clear_tags_buffer)
    applicationView = ApplicationView(applicationStateMachine)
    applicationStateMachine.start()
    
    applicationView.showFullScreen()
    sys.exit(app.exec())

#===========================================================================

