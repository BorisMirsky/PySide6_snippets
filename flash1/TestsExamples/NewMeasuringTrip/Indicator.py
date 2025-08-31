# This Python file uses the following encoding: utf-8
from PySide6.QtGui import QPainter, QColor, QPolygon, QPaintEvent, QConicalGradient, QGradient, QBrush, QRegion, QResizeEvent
from PySide6.QtCore import Signal, QSize, QRect, QPoint, Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QLabel
from domain.units.AbstractUnit import AbstractReadUnit
from typing import List, Tuple
import numpy


# Обычный
class ArrowPointerIndicator(QWidget):
    #minimumValueChange: Signal = Signal(float)
    #maximumValueChange: Signal = Signal(float)
    #model: AbstractReadUnit[float]
    changed: Signal = Signal(float)
    def __init__(self, #model: AbstractReadUnit[float],
                 chunks: List[Tuple[float, QColor]],
                 lineWidth: int = 5,
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        #self.model: AbstractReadUnit[float] = model
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

        self.__minimum = -90.0
        self.__maximum = 90.0
        self.__lineWidth = lineWidth
        self.__value: float = 0.0

    def valueRange(self) ->(float, float):
        return (self.__minimum, self.__maximum)

    def setValueRange(self, minimum: float, maximum: float) ->None:
        if self.__minimum != minimum:
            self.__minimum = minimum
            self.update()
        if self.__maximum != maximum:
            self.__maximum = maximum
            self.update()

    def value(self) ->float:
        return self.__value

    def setValue(self, value: float) ->None:
        if self.__value == value:
            return
        self.__value = max(min(value, self.__maximum), self.__minimum)
        self.changed.emit(self.__value)
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
        painter.drawRect(self.width() / 2.5, 10, self.width() / 5, 30) # 20, 10, 70, 30)  # Рисование прямоугольника
        value = str(round(self.__value, 3))
        painter.drawText(self.width() / 2.5, 30, value)
        #
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        painter.save()
        outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
        painter.setClipRegion(outerRegion)
        painter.setBrush(QBrush(self.__gradient))
        painter.drawChord(drawingRect, 0, 180 * 16)
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        painter.rotate(float(numpy.interp(self.__value, self.valueRange(), (-90, 90))))
        painter.drawConvexPolygon(self.__arrow)
        painter.restore()


# цветной, с тремя окошками
class ArrowPointerControlLevelIndicator(QWidget):
    changed: Signal = Signal(float)
    def __init__(self, #model: AbstractReadUnit[float],
                 chunks: List[Tuple[float, QColor]],
                 lineWidth: int = 5,
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        #self.model: AbstractReadUnit[float] = model
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

        self.__minimum = -90.0
        self.__maximum = 90.0
        self.__lineWidth = lineWidth
        self.__value: float = 0.0

    def valueRange(self) ->(float, float):
        return (self.__minimum, self.__maximum)

    def setValueRange(self, minimum: float, maximum: float) ->None:
        if self.__minimum != minimum:
            self.__minimum = minimum
            self.update()
        if self.__maximum != maximum:
            self.__maximum = maximum
            self.update()

    def value(self) ->float:
        return self.__value

    def setValue(self, value: float) ->None:
        if self.__value == value:
            return
        self.__value = max(min(value, self.__maximum), self.__minimum)
        self.changed.emit(self.__value)
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
        painter.setBrush(QColor(Qt.GlobalColor.darkGray))   # black
        painter.drawRect(self.width() / 2.5, 10, 40, 30)
        value = str(round(self.__value, 3))
        painter.drawText(self.width() / 2.5 + 5, 30, value)
        #
        painter.setBrush(QColor(Qt.GlobalColor.darkGray))
        painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 40, 30)
        value1 = "123"
        painter.drawText(self.width() - (self.width() / 10) - 15, 30, value1)
        #
        painter.setBrush(QColor(Qt.GlobalColor.darkGray))
        painter.drawRect(self.width() - (self.width() / 10) - 20, self.height() - (self.height() / 10),
                         self.width() / 30, 30)
        value2 = "456"
        painter.drawText(self.width() - (self.width() / 10) + 20, self.height() - (self.height() / 10) - 20, value2)
        #
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        painter.save()
        outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
        painter.setClipRegion(outerRegion)
        painter.setBrush(QBrush(self.__gradient))
        painter.drawChord(drawingRect, 0, 180 * 16)
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        painter.rotate(float(numpy.interp(self.__value, self.valueRange(), (-90, 90))))
        painter.drawConvexPolygon(self.__arrow)
        painter.restore()



# Большой с тремя кнопками
class ArrowPointerStrelographWorkIndicator(QWidget):
    changed: Signal = Signal(float)
    def __init__(self, #model: AbstractReadUnit[float],
                 chunks: List[Tuple[float, QColor]],
                 lineWidth: int = 5,
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        #self.model: AbstractReadUnit[float] = model
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

        self.__minimum = -90.0
        self.__maximum = 90.0
        self.__lineWidth = lineWidth
        self.__value: float = 0.0

    def valueRange(self) ->(float, float):
        return (self.__minimum, self.__maximum)

    def setValueRange(self, minimum: float, maximum: float) ->None:
        if self.__minimum != minimum:
            self.__minimum = minimum
            self.update()
        if self.__maximum != maximum:
            self.__maximum = maximum
            self.update()

    def value(self) ->float:
        return self.__value

    def setValue(self, value: float) ->None:
        if self.__value == value:
            return
        self.__value = max(min(value, self.__maximum), self.__minimum)
        self.changed.emit(self.__value)
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
        painter.drawRect(self.width() / 2.5, 10, self.width() / 5, 30) # 20, 10, 70, 30)  # Рисование прямоугольника
        value = str(round(self.__value, 3))
        painter.drawText(self.width() / 2.5, 30, value)
        #
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        painter.save()
        outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
        painter.setClipRegion(outerRegion)
        painter.setBrush(QBrush(self.__gradient))
        painter.drawChord(drawingRect, 0, 180 * 16)
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        painter.rotate(float(numpy.interp(self.__value, self.valueRange(), (-90, 90))))
        painter.drawConvexPolygon(self.__arrow)
        painter.restore()


class SizeBoundedWindow(QWidget):
    def __init__(self, scale: float = 1, parent: QWidget = None) ->None:
        super().__init__(parent)
        self.__scale: float = scale
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHeightForWidth(True)
        self.setSizePolicy(sizePolicy)

    def sizeHint(self) ->QSize:
        return QSize(self.width(), self.heightForWidth(self.width()));
    def heightForWidth(self, width: int) ->int:
        return int(width * self.__scale)


    # def sizeHint(self) ->QSize:
    #     return QSize(self.width(), self.width() * self.__scale)
    # def hasHeightForWidth(self) -> bool:
    #     return True
    # def heightForWidth(self, width: int) ->int:
    #     return width * self.__scale


# if __name__ == '__main__':
#     from PySide6.QtWidgets import QApplication
#     import sys
#     app = QApplication(sys.argv)
#     window = ArrowPointerControlLevelIndicator(chunks =[
#         (1, QColor(255, 0, 0)),
#         (5, QColor(255, 255, 0)),
#         (3, QColor(0, 255, 0)),
#         (5, QColor(255, 255, 0)),
#         (1, QColor(255, 0, 0)),
#     ], lineWidth = 4)
#     window.show()
#     sys.exit(app.exec())
#

