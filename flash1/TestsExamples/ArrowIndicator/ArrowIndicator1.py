from PySide6.QtGui import QPainter, QColor, QPolygon, QPen, QPaintEvent, QConicalGradient, QGradient, QBrush, QRegion, QResizeEvent, QPainterPath
from PySide6.QtCore import Signal, QSize, QRect, QPoint, Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QLabel
from typing import List, Tuple
import numpy


# цветной, с тремя окошками
class ArrowPointerControlLevelIndicator(QWidget):
    changed: Signal = Signal(float)
    def __init__(self,
                 chunks: List[Tuple[float, QColor]],
                 lineWidth: int = 5,
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        self.__arrowColor: QColor = QColor(255, 0, 0)
        self.__gradient: QGradient = None
        self.setChunks(chunks)
        self.__arrow = QPolygon([
            QPoint(-2, -80),
            QPoint(0, -100),
            QPoint(2, -80),
            QPoint(2, 10),
            QPoint(-2, 10),
            QPoint(-2, -80)
        ])
        self.__minimum = -10.0
        self.__maximum = 10.0
        self.__lineWidth = lineWidth
        self.__value1: float = 0.0      # arrowIndicator
        self.__value2: float = 0.0      # frame with value top   "Натурное значение контрольного маятника;"
        self.__value3: float = 0.0      # frame with value bottom  "Проектное значение контрольного маятника;"

    def valueRange(self) ->(float, float):
        return (self.__minimum, self.__maximum)

    def setValueRange(self, minimum: float, maximum: float) ->None:
        if self.__minimum != minimum:
            self.__minimum = minimum
            self.update()
        if self.__maximum != maximum:
            self.__maximum = maximum
            self.update()

    def value1(self) ->float:
        return self.__value1
    def value2(self) ->float:
        return self.__value2
    def value3(self) ->float:
        return self.__value3

    def setValue1(self, value: float) ->None:
        if self.__value1 == value:
            return
        self.__value1 = value
        self.changed.emit(self.__value1)
        self.update()
    def setValue2(self, value: float) ->None:
        if self.__value2 == value:
            return
        self.__value2 = value
        self.changed.emit(self.__value2)
        self.update()
    def setValue3(self, value: float) ->None:
        if self.__value3 == value:
            return
        self.__value3 = value
        self.changed.emit(self.__value3)
        self.update()

    def lineWidth(self) ->int:
        return self.__lineWidth

    def setLineWidth(self, lineWidth: int) ->None:
        if self.__lineWidth == lineWidth:
            return
        self.__lineWidth = lineWidth
        self.update()

    def arrowColor(self) ->QColor:
        return self.__arrowColor

    def setArrowColor(self, arrowColor: QColor) ->QColor:
        if self.__arrowColor == arrowColor:
            return
        self.__arrowColor = arrowColor
        self.update()

    def setChunks(self, chunks: List[Tuple[float, QColor]]) ->None:
        weightsSum: float = sum(item[0] for item in chunks)
        chunks = [(item[0] / weightsSum / 2, item[1]) for item in chunks]
        self.__gradient = QConicalGradient()
        passedWeight = 0.25
        for weight, color in chunks:
            self.__gradient.setColorAt(passedWeight, color)
            self.__gradient.setColorAt(passedWeight + weight - 0.0000000001, color)
            passedWeight += weight
        self.__gradient.setCenter(QPoint(0, 0))
        self.__gradient.setAngle(-90)
        self.update()

    def paintEvent(self, event: QPaintEvent) ->None:
        super().paintEvent(event)
        drawSize = min(self.width() / 2, self.height())
        painter = QPainter(self)
        painter.drawRect(QRect(1, 1, self.width() - 2, self.height() - 2))
        #
        painter.setBrush(QColor('#ebbf58'))
        painter.drawRect((self.width() / 2) - 30, 10, 50, 30)
        value1 = str(round(self.__value1, 1))
        painter.drawText((self.width() / 2) - 25, 30, value1)
        #
        control_level_label = "Контрольный уровень"
        painter.setPen(QColor('black'))
        painter.drawText((self.width() / 2) + 80, 60, control_level_label)
        #
        painter.setBrush(QColor('black'))
        painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 50, 30)
        painter.setPen(QColor('white'))
        value2 = str(round(self.__value2, 1))
        painter.drawText(self.width() - (self.width() / 10) - 15, 30, value2)
        #
        vozv_label = "Возвышение"
        painter.setPen(QColor('black'))
        painter.drawText((self.width() / 2) + 70, self.height() - (self.height() / 10), vozv_label)
        #
        painter.setBrush(QColor('black'))
        painter.drawRect(self.width() - (self.width() / 10) - 20, self.height() - (self.height() / 10 + 15), 50, 30)
        painter.setPen(QColor('white'))
        value3 = str(round(self.__value3, 1))
        painter.drawText(self.width() - (self.width() / 10) - 15, self.height() - (self.height() / 10 - 10), value3)
        #
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
        painter.setClipRegion(outerRegion)
        painter.setBrush(QBrush(self.__gradient))
        painter.drawChord(drawingRect, 0, 180 * 16)
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        painter.rotate(float(numpy.interp(self.__value1, self.valueRange(), (-90, 90))))
        painter.drawConvexPolygon(self.__arrow)
        painter.setPen(QPen(Qt.GlobalColor.black, 10))


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ArrowPointerControlLevelIndicator(
        chunks=[
            (2, Qt.GlobalColor.red),
            (7, Qt.GlobalColor.yellow),
            (3, Qt.GlobalColor.green),
            (7, Qt.GlobalColor.yellow),
            (2, Qt.GlobalColor.red),
        ], lineWidth=4)
    window.show()
    sys.exit(app.exec())