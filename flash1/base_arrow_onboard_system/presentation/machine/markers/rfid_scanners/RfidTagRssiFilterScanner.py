# This Python file uses the following encoding: utf-8
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from PySide6.QtCore import QTimerEvent, QThread, QObject
from typing import Optional, Dict, List
from dataclasses import dataclass
import time

class RfidTagRssiFilterScanner(AbstractRfidScanner):
    @dataclass(frozen = True)
    class RfidTagWaitBuffer:
        tag: RailwayMarker
        rssi: float#На самом деле int, но пусть будет float
        last_update_time: int
        is_sended_flag: bool

    def __init__(self, scanners: List[AbstractRfidScanner], check_timeout_ms: int = 50, expire_timeout_ms: int = 1000, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__scanners: List[AbstractRfidScanner] = scanners
        self.__storage: Dict[str, RfidTagRssiFilterScanner.RfidTagWaitBuffer] = {}
        self.__expire_timeout: int = expire_timeout_ms/1000
        self.startTimer(check_timeout_ms)

        for scanner in self.__scanners:
            scanner.tagReceived.connect(self.rfid_tag_received)

    def timerEvent(self, event: QTimerEvent) ->None:
        super().timerEvent(event)
        self.check_expired_tags()

    def rfid_tag_received(self, tag: RailwayMarker, rssi: float) ->None:
        # print(f'rfid_tag_received = {tag, rssi}')
        if tag.title not in self.__storage:
            self.__storage[tag.title] = RfidTagRssiFilterScanner.RfidTagWaitBuffer(
                last_update_time = time.time(),
                tag = tag, rssi = rssi,
                is_sended_flag = False
            )
        elif rssi > self.__storage[tag.title].rssi * 1.1:
            self.__storage[tag.title] = RfidTagRssiFilterScanner.RfidTagWaitBuffer(
                is_sended_flag = self.__storage[tag.title].is_sended_flag,
                last_update_time = time.time(),
                tag = tag, rssi = rssi
            )
        elif not self.__storage[tag.title].is_sended_flag and rssi < self.__storage[tag.title].rssi / 1.1:
            self.__storage[tag.title] = RfidTagRssiFilterScanner.RfidTagWaitBuffer(
                last_update_time = time.time(),
                tag = tag, rssi = rssi,
                is_sended_flag = True
            )
            self.tagReceived.emit(tag, rssi)
    def clear_tags_buffer(self) ->None:
        self.__storage = {}
    def check_expired_tags(self) ->None:
        current_time: int = time.time()
        for tag_id, tag_buffer in self.__storage.items():
            if tag_buffer.is_sended_flag:
                continue
            if tag_buffer.last_update_time + self.__expire_timeout > current_time:
                continue

            self.__storage[tag_id] = RfidTagRssiFilterScanner.RfidTagWaitBuffer(
                last_update_time = tag_buffer.last_update_time,
                tag = tag_buffer.tag, rssi = tag_buffer.rssi,
                is_sended_flag = True
            )
            self.tagReceived.emit(tag_buffer.tag, tag_buffer.rssi)
