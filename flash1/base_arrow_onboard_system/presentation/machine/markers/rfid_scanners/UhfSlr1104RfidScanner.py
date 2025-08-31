# This Python file uses the following encoding: utf-8
from domain.dto.Markers import RailwayMarker, RailwayMarkerType, RailwayMarkerLocation
from domain.markers.AbstractRfidScanner import AbstractRfidScanner
from PySide6.QtCore import QCoreApplication, QThread, QObject
from typing import Optional
from aiohttp import web
import aiohttp
import asyncio



class UhfSlr1104RfidScanner(AbstractRfidScanner):
    class InternalRfidTabWebServer(QThread):
        def __init__(self, host: str, port: int, parent: AbstractRfidScanner) ->None:
            super().__init__(parent)
            QCoreApplication.instance().aboutToQuit.connect(self.stop_and_wait)
            self.__scanner = parent
            self.__host: str = host
            self.__port: int = port

        def run(self) ->None:
            asyncio.run(self.__run_tags_listener())
        def stop_and_wait(self) ->None:
            self.requestInterruption()
            self.wait()

        async def __post_current_rfid_tag(self, request: aiohttp.web_request.Request):
            print('Request to update current rfid tag: ', request, await request.text())
            request_data = await request.json()
            if 'tag_id' not in request_data:
                return web.Response(text = 'Invalid request: has no "tag_id"', status = 400)#bad request

            self.__scanner.tagReceived.emit(RailwayMarker(
                title = str(request_data["tag_id"]),
                type = RailwayMarkerType.RfidTag,
                location = RailwayMarkerLocation.Middle 
            ), float(request_data["rssi"]))
            return web.Response(status = 200)#ok
        async def __run_tags_listener(self) ->None:
            app = web.Application()
            app.add_routes([web.post('/', self.__post_current_rfid_tag)])
            app.add_routes([web.get('/', lambda _: web.Response(text="Ok"))])
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, self.__host, self.__port)
            await site.start()

            while not self.isInterruptionRequested():
                await asyncio.sleep(1)
    def __init__(self, host: str, port: int, parent: Optional[QObject] = None) ->None:
        super().__init__(parent)
        self.__server = UhfSlr1104RfidScanner.InternalRfidTabWebServer(host, port, self)
        self.__server.start(QThread.Priority.LowPriority)



