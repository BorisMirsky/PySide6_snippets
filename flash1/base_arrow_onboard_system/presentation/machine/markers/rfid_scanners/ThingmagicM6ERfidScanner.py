# This Python file uses the following encoding: utf-8
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from PySide6.QtCore import QCoreApplication, QThread, QObject
from typing import Optional, List
import mercury

class ThingmagicM6ERfidScanner(AbstractRfidScanner):
    class InternalThingmagicM6ERfidScannerReader(QThread):
        def __init__(self, host: str, antennas: List[int], protocol: str, region: str, parent: Optional[QObject] = None) ->None:
            super().__init__(parent)
            print('Start reader initialization...')
            QCoreApplication.instance().aboutToQuit.connect(self.stop_and_wait)
            try:
                self.__reader = mercury.Reader(host)
                self.__reader.set_read_plan(antennas, protocol)
                self.__reader.set_region(region)
            except:
                self.__reader = None

        def stop_and_wait(self) ->None:
            self.requestInterruption()
            self.wait()

        def run(self) ->None:
            if self.__reader is None:
                return

            while not self.isInterruptionRequested():
                try:
                    for tag in self.__reader.read(500):
                        self.tagReceived.emit(RailwayMarker(
                            title = tag.epc.decode('utf-8'), 
                            type = RailwayMarkerType.RfidTag,
                            location = RailwayMarkerLocation.Middle
                        ), tag.rssi)
                except Exception as error:
                    print(f'[M6E][Error occured: {error}]')

    def __init__(self, host: str, antennas: List[int], protocol: str, region: str, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__reader = ThingmagicM6ERfidScanner.InternalThingmagicM6ERfidScannerReader(host, antennas, protocol, region, self)