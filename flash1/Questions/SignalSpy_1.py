from PySide6.QtTest import QSignalSpy
from PySide6.QtCore import QObject, QUrl  #, pyqtSlot
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager


class HttpRequest(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_access_man = QNetworkAccessManager(self)
        self.network_access_man.finished.connect(self.finished)

    def get(self, url):
        req = QNetworkRequest(QUrl(url))
        self.network_access_man.get(req)

    #@pyqtSlot(QNetworkReply)
    def finished(self, reply):
        reply_error = reply.error()
        print("reply error: {}".format(reply_error))
        if reply_error == QNetworkReply.NoError:
            reply_content = reply.readAll()
            print("content:\n{}\n".format(reply_content[0:20]))
        else:
            print("Reply error...")


if __name__ == "__main__":
    app = QApplication([])
    http_req = HttpRequest()
    http_req.get("https://www.python.org/static/files/pubkeys.txt")
    spy = QSignalSpy(http_req.network_access_man.finished)
    print("Spy signal: {}".format(spy.signal()))
    print("Spy isValid:", spy.isValid())
    print("Spy wait return value: {}".format(spy.wait(5000)))   # timeout
    #if len(spy) > 0:
    #    print("Spy length: {}".format(len(spy)))
    #    print(spy[0])
    #else:
    #    print("spy is empty")