# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QEasingCurve, QElapsedTimer, QTimerEvent, QRect, qFuzzyCompare
from PySide6.QtGui import QPaintEvent, QPainter, QColor
from PySide6.QtWidgets import QWidget


class CircliBusyIndicator(QWidget):
    def __init__(self, colors = (QColor("#dc322f"), QColor("#268bd2"), QColor("#2aa198")), line_count: int = 10, parent: QWidget = None) ->None:
        super().__init__(parent)
        self.__line_count = line_count
        self.__colors = colors
        self.__elapsed_timer = QElapsedTimer()
        self.__timer_id = 0

    def colors(self) ->(QColor, QColor, QColor):
        return self.__colors
    def setColors(self, colors: (QColor, QColor, QColor)) ->None:
        self.__colors = colors
        if self.__timer_id != 0:
            self.update()
    def lineCount(self) ->int:
        return self.__line_count
    def setLineCount(self, line_count: int) ->None:
        self.__line_count = line_count
        if self.__timer_id != 0:
            self.update()

    def start(self) ->None:
        if self.__timer_id == 0:
            self.__timer_id = self.startTimer(1000.0 / 60)
            self.__elapsed_timer.restart()
    def stop(self) ->None:
        if self.__timer_id != 0:
            self.killTimer(self.__timer_id)
            self.__timer_id = 0

    def timerEvent(self, event: QTimerEvent) ->None:
        super().timerEvent(event)
        if event.timerId() == self.__timer_id:
            self.update()

    def paintEvent(self, event: QPaintEvent) ->None:
        super().paintEvent(event)
        msecs: int = self.__elapsed_timer.elapsed() % 5000
        inverted: bool = msecs > 2500
        msecs %= 2500

        headCurve: QEasingCurve = QEasingCurve(QEasingCurve.Type.OutQuad)
        tailCurve: QEasingCurve = QEasingCurve(QEasingCurve.Type.InQuad)

        r0: QRect = self.rect();
        if r0.width() > r0.height():
            r0.setWidth(r0.height())
        else:
            r0.setHeight(r0.width())

        r0.moveCenter(self.rect().center())

        painter: QPainter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        for line in range(self.__line_count):
            k1: float = min(msecs / (1000.0 + 1000.0 / self.__line_count * line), 1.0)
            k2: float = min(msecs / (1500.0 + 1000.0 / self.__line_count * line), 1.0)
            if qFuzzyCompare(k1, k2):
                continue

            if inverted:
                headAngle: float = 90 - headCurve.valueForProgress(k1) * 360
                tailAngle: float = 90 - tailCurve.valueForProgress(k2) * 360
            else:
                headAngle: float = 90 + headCurve.valueForProgress(k1) * 360
                tailAngle: float = 90 + tailCurve.valueForProgress(k2) * 360

            spanAngle: float = tailAngle - headAngle;

            r1: QRect = QRect(r0)
            r1.setSize(r0.size() * (1.0 / self.__line_count * (self.__line_count - line)))
            r1.moveCenter(r0.center())
            r2: QRect = QRect(r0)
            r2.setSize(r0.size() * (1.0 / self.__line_count * (self.__line_count - line - 1) + 0.01))
            r2.moveCenter(r0.center())

            l1: float = 1.0 - headCurve.valueForProgress(k1)
            l3: float = tailCurve.valueForProgress(k1)
            l2: float = 1.0 - l1 - l3


            painter.setBrush(self.__colors[0])
            painter.drawPie(r1, headAngle * 16, spanAngle * 16 * l1 * 0.9)
            painter.drawPie(r2, headAngle * 16, spanAngle * 16 * l1 * 0.9)

            painter.setBrush(self.__colors[1])
            painter.drawPie(r1, headAngle * 16 + spanAngle * 16 * l1, spanAngle * 16 * l2 * 0.9)
            painter.drawPie(r2, headAngle * 16 + spanAngle * 16 * l1, spanAngle * 16 * l2 * 0.9)

            painter.setBrush(self.__colors[2])
            painter.drawPie(r1, headAngle * 16 + spanAngle * 16 * (l1 + l2), spanAngle * 16 * l3 * 0.9)
            painter.drawPie(r2, headAngle * 16 + spanAngle * 16 * (l1 + l2), spanAngle * 16 * l3 * 0.9)

# if __name__ == '__main__':
#     from PySide6.QtWidgets import QApplication
#     import sys
#     app = QApplication(sys.argv)
#     window = CircliBusyIndicator()
#     window.setLineCount(10)
#     window.start()
#     window.show()
#     app.exec()
