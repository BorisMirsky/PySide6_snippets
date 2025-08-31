# This Python file uses the following encoding: utf-8
from PySide6.QtGui import QPainter, QColor, QPolygon, QPen, QPaintEvent, QConicalGradient, QGradient, QBrush, QRegion, QResizeEvent, QPainterPath
from PySide6.QtCore import Signal, QSize, QRect, QPoint, Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QLabel
from typing import List, Tuple
import numpy


# 'Обычный', 3 штуки (большой и 2 маленьких)
class ArrowPointerIndicator(QWidget):
    changed: Signal = Signal(float)
    def __init__(self, chunks: List[Tuple[float, QColor]],
                 lineWidth: int,
                 indicatorType: str,
                 inverse_arrow_rotation: bool = False,
                 parent: QWidget = None) ->None:
        super().__init__(parent)
        self.__arrowColor: QColor = QColor(0, 0, 0)
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
        if indicatorType == 'controlLevelIndicator':
            self.__value1: float = 0.0  # arrowIndicator
            self.__value2: float = 0.0  # "Натурное значение контрольного маятника;"
            self.__value3: float = 0.0  # "Проектное значение контрольного маятника;"
        elif indicatorType =='strelographWorkIndicator':
            self.__value4: float = 0.0  #
            self.__value5: float = 0.0  # satellite
            self.state_button_1 = 0
            self.state_button_2 = 0
            self.state_button_3 = 0
            self.color_red = "#FF0000"
            self.color_green = "#00FF7F"
        elif indicatorType =='commonIndicator':
            self.__value: float = 0.0
        self.indicatorType = indicatorType
        self.__ratationRange = (-90, 90) if not inverse_arrow_rotation else (90, -90)

    def valueRange(self) ->Tuple[float, float]:
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
        self.__value = value
        self.changed.emit(self.__value)
        self.update()

    def value1(self) ->float:
        return self.__value1
    def setValue1(self, value: float) ->None:
        if self.__value1 == value:
            return
        self.__value1 = value
        self.changed.emit(self.__value1)
        self.update()

    def value2(self) ->float:
        return self.__value2
    def setValue2(self, value: float) ->None:
        if self.__value2 == value:
            return
        self.__value2 = value
        self.changed.emit(self.__value2)
        self.update()

    def value3(self) ->float:
        return self.__value3
    def setValue3(self, value: float) ->None:
        if self.__value3 == value:
            return
        self.__value3 = value
        self.changed.emit(self.__value3)
        self.update()

    def value4(self) ->float:
        return self.__value4
    def setValue4(self, value: float) ->None:
        if self.__value4 == value:
            return
        self.__value4 = value
        self.changed.emit(self.__value4)
        self.update()

    def value5(self) ->float:
        return self.__value5
    def setValue5(self, value: float) ->None:
        if self.__value5 == value:
            return
        self.__value5 = value
        self.changed.emit(self.__value5)
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
        painter.setBrush(QColor('#ebbf58'))
        painter.drawRect((self.width() / 2) - 30, 10, 50, 30)
        if self.indicatorType == 'controlLevelIndicator':
            value1 = str(round(self.__value1, 1))
            painter.drawText((self.width() / 2) - 25, 30, value1)
            control_level_label = "Контрольный уровень"
            painter.setPen(QColor('black'))
            painter.drawText((self.width() / 2) + 80, 60, control_level_label)
            painter.setBrush(QColor('black'))
            painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 50, 30)
            painter.setPen(QColor('white'))
            value2 = str(round(self.__value2, 1))
            painter.drawText(self.width() - (self.width() / 10) - 15, 30, value2)
            vozv_label = "Возвышение"
            painter.setPen(QColor('black'))
            painter.drawText((self.width() / 2) + 70, self.height() - (self.height() / 10), vozv_label)
            painter.setBrush(QColor('black'))
            painter.drawRect(self.width() - (self.width() / 10) - 20, self.height() - (self.height() / 10 + 15), 50, 30)
            painter.setPen(QColor('white'))
            value3 = str(round(self.__value3, 1))
            painter.drawText(self.width() - (self.width() / 10) - 15, self.height() - (self.height() / 10 - 10), value3)
        elif self.indicatorType == 'strelographWorkIndicator':
            value4 = str(round(self.__value4, 1))
            painter.drawText((self.width() / 2) - 25, 30, value4)
            satellite_label = "Сателит"
            painter.setPen(QColor('black'))
            painter.drawText((self.width() / 2) + 150, 30, satellite_label)
            painter.setBrush(QColor('black'))
            painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 50, 30)
            value5 = str(round(self.__value5, 1))
            painter.setPen(QColor('white'))
            painter.drawText(self.width() - (self.width() / 10) - 15, 30, value5)
            if self.state_button_1:
                painter.setBrush(QBrush(QColor(self.color_green)))
            else:
                painter.setBrush(QBrush(QColor(self.color_red)))
            painter.drawEllipse(50, 50, 20, 20)
            if self.state_button_2:
                painter.setBrush(QBrush(QColor(self.color_green)))
            else:
                painter.setBrush(QBrush(QColor(self.color_red)))
            painter.drawEllipse(30, 70, 20, 20)
            if self.state_button_3:
                painter.setBrush(QBrush(QColor(self.color_green)))
            else:
                painter.setBrush(QBrush(QColor(self.color_red)))
            painter.drawEllipse(70, 70, 20, 20)
        elif self.indicatorType == 'commonIndicator':
            value = str(round(self.__value, 1))
            painter.drawText((self.width() / 2) - 25, 30, value)
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        if self.indicatorType == 'controlLevelIndicator':
            excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth,
                                2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
            outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(
                QRegion(excludeRect, QRegion.RegionType.Ellipse))
            painter.setClipRegion(outerRegion)
            painter.setBrush(QBrush(self.__gradient))
            painter.drawChord(drawingRect, 0, 180 * 16)
        else:
            path = QPainterPath()
            path.addEllipse(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
            painter.setBrush(QBrush(self.__gradient))
            painter.drawChord(drawingRect, 0, 180 * 16)  #drawPie
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        if self.indicatorType == 'controlLevelIndicator':
            painter.rotate(float(numpy.interp(self.__value1, self.valueRange(), self.__ratationRange)))
        elif self.indicatorType == 'strelographWorkIndicator':
            painter.rotate(float(numpy.interp(self.__value4, self.valueRange(), self.__ratationRange)))
        elif self.indicatorType == 'commonIndicator':
            painter.rotate(float(numpy.interp(self.__value, self.valueRange(), self.__ratationRange)))
        painter.drawConvexPolygon(self.__arrow)
        painter.restore()


# # цветной, с тремя окошками, 1 штука
# class ArrowPointerControlLevelIndicator(QWidget):
#     changed: Signal = Signal(float)
#     def __init__(self,
#                  chunks: List[Tuple[float, QColor]],
#                  lineWidth: int,
#                  parent: QWidget = None) ->None:
#         super().__init__(parent)
#         self.__arrowColor: QColor = QColor(255, 0, 0)
#         self.__gradient: QGradient = None
#         self.setChunks(chunks)
#         self.__arrow = QPolygon([
#             QPoint(-2, -80),
#             QPoint(0, -100),
#             QPoint(2, -80),
#             QPoint(2, 10),
#             QPoint(-2, 10),
#             QPoint(-2, -80)
#         ])
#
#         self.__minimum = -10.0
#         self.__maximum = 10.0
#         self.__lineWidth = lineWidth
#         self.__value1: float = 0.0      # arrowIndicator
#         self.__value2: float = 0.0      # frame with value top   "Натурное значение контрольного маятника;"
#         self.__value3: float = 0.0      # frame with value bottom  "Проектное значение контрольного маятника;"
#
#     def valueRange(self) ->(float, float):
#         return (self.__minimum, self.__maximum)
#
#     def setValueRange(self, minimum: float, maximum: float) ->None:
#         if self.__minimum != minimum:
#             self.__minimum = minimum
#             self.update()
#         if self.__maximum != maximum:
#             self.__maximum = maximum
#             self.update()
#     def value1(self) ->float:
#         return self.__value1
#     def value2(self) ->float:
#         return self.__value2
#     def value3(self) ->float:
#         return self.__value3
#
#     def setValue1(self, value: float) ->None:
#         if self.__value1 == value:
#             return
#         self.__value1 = value
#         self.changed.emit(self.__value1)
#         self.update()
#     def setValue2(self, value: float) ->None:
#         if self.__value2 == value:
#             return
#         self.__value2 = value
#         self.changed.emit(self.__value2)
#         self.update()
#     def setValue3(self, value: float) ->None:
#         if self.__value3 == value:
#             return
#         self.__value3 = value
#         self.changed.emit(self.__value3)
#         self.update()
#     def lineWidth(self) ->int:
#         return self.__lineWidth
#     def setLineWidth(self, lineWidth: int) ->None:
#         if self.__lineWidth == lineWidth:
#             return
#         self.__lineWidth = lineWidth
#         self.update()
#     def arrowColor(self) ->QColor:
#         return self.__arrowColor
#     def setArrowColor(self, arrowColor: QColor) ->QColor:
#         if self.__arrowColor == arrowColor:
#             return
#         self.__arrowColor = arrowColor
#         self.update()
#     def setChunks(self, chunks: List[Tuple[float, QColor]]) ->None:
#         weightsSum: float = sum(item[0] for item in chunks)
#         chunks = [(item[0] / weightsSum / 2, item[1]) for item in chunks]
#         self.__gradient = QConicalGradient()
#         passedWeight = 0.25
#         for weight, color in chunks:
#             self.__gradient.setColorAt(passedWeight, color)
#             self.__gradient.setColorAt(passedWeight + weight - 0.0000000001, color)
#             passedWeight += weight
#         self.__gradient.setCenter(QPoint(0, 0))
#         self.__gradient.setAngle(-90)
#         self.update()
#     def paintEvent(self, event: QPaintEvent) ->None:
#         super().paintEvent(event)
#         drawSize = min(self.width() / 2, self.height())
#         painter = QPainter(self)
#         painter.drawRect(QRect(1, 1, self.width() - 2, self.height() - 2))
#         painter.setBrush(QColor('#ebbf58'))
#         painter.drawRect((self.width() / 2) - 30, 10, 50, 30)
#         value1 = str(round(self.__value1, 1))
#         painter.drawText((self.width() / 2) - 25, 30, value1)
#         control_level_label = "Контрольный уровень"
#         painter.setPen(QColor('black'))
#         painter.drawText((self.width() / 2) + 80, 60, control_level_label)
#         painter.setBrush(QColor('black'))
#         painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 50, 30)
#         painter.setPen(QColor('white'))
#         value2 = str(round(self.__value2, 1))
#         painter.drawText(self.width() - (self.width() / 10) - 15, 30, value2)
#         vozv_label = "Возвышение"
#         painter.setPen(QColor('black'))
#         painter.drawText((self.width() / 2) + 70, self.height() - (self.height() / 10), vozv_label)
#         painter.setBrush(QColor('black'))
#         painter.drawRect(self.width() - (self.width() / 10) - 20, self.height() - (self.height() / 10 + 15), 50, 30)
#         painter.setPen(QColor('white'))
#         value3 = str(round(self.__value3, 1))
#         painter.drawText(self.width() - (self.width() / 10) - 15, self.height() - (self.height() / 10 - 10), value3)
#         painter.translate(self.width() / 2, self.height())
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         self.__drawColorArc(drawSize, painter)
#         self.__drawArrowPointer(drawSize, painter)
#
#     def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
#         painter.save()
#         path = QPainterPath()   #
#         drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
#         excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
#         outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
#         painter.setClipRegion(outerRegion)
#         painter.setBrush(QBrush(self.__gradient))
#         painter.drawChord(drawingRect, 0, 180 * 16)
#         painter.restore()
#
#     def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
#         painter.save()
#         painter.setBrush(self.__arrowColor)
#         painter.scale(drawSize / 100.0, drawSize / 100.0)
#         painter.rotate(float(numpy.interp(self.__value1, self.valueRange(), (-90, 90))))
#         painter.drawConvexPolygon(self.__arrow)
#         painter.restore()
#
#
# # Большой с тремя круглыми кнопками + метка 'сателлит', 1 штука
# class ArrowPointerStrelographWorkIndicator(QWidget):
#     changed: Signal = Signal(float)
#     def __init__(self,
#                  chunks: List[Tuple[float, QColor]],
#                  lineWidth: int,
#                  parent: QWidget = None) ->None:
#         super().__init__(parent)
#         self.__arrowColor: QColor = QColor(255, 0, 0)
#         self.__gradient: QGradient = None
#         self.setChunks(chunks)
#         self.__arrow = QPolygon([
#             QPoint(-2, -80),
#             QPoint(0, -100),
#             QPoint(2, -80),
#             QPoint(2, 10),
#             QPoint(-2, 10),
#             QPoint(-2, -80)
#         ])
#         self.__minimum = -10.0
#         self.__maximum = 10.0
#         self.__lineWidth = lineWidth
#         self.__value1: float = 0.0          #
#         self.__value2: float = 0.0          # satellite
#         self.state_button_1 = 0
#         self.state_button_2 = 0
#         self.state_button_3 = 0
#         self.color_red = "#FF0000"
#         self.color_green = "#00FF7F"
#
#     def valueRange(self) ->(float, float):
#         return (self.__minimum, self.__maximum)
#
#     def setValueRange(self, minimum: float, maximum: float) ->None:
#         if self.__minimum != minimum:
#             self.__minimum = minimum
#             self.update()
#         if self.__maximum != maximum:
#             self.__maximum = maximum
#             self.update()
#
#     def value1(self) ->float:
#         return self.__value1
#
#     def value2(self) ->float:
#         return self.__value2
#
#     def setValue1(self, value1: float) ->None:
#         if self.__value1 == value1:
#             return
#         self.__value1 = value1
#         self.changed.emit(self.__value1)
#         self.update()
#     def setValue2(self, value2: float) ->None:
#         if self.__value2 == value2:
#             return
#         self.__value2 = value2
#         self.changed.emit(self.__value2)
#         self.update()
#     def lineWidth(self) ->int:
#         return self.__lineWidth
#     def setLineWidth(self, lineWidth: int) ->None:
#         if self.__lineWidth == lineWidth:
#             return
#         self.__lineWidth = lineWidth
#         self.update()
#     def arrowColor(self) ->QColor:
#         return self.__arrowColor
#     def setArrowColor(self, arrowColor: QColor) ->QColor:
#         if self.__arrowColor == arrowColor:
#             return
#         self.__arrowColor = arrowColor
#         self.update()
#     def setChunks(self, chunks: List[Tuple[float, QColor]]) ->None:
#         weightsSum: float = sum(item[0] for item in chunks)
#         chunks = [(item[0] / weightsSum / 2, item[1]) for item in chunks]
#         self.__gradient = QConicalGradient()
#         passedWeight = 0.25
#         for weight, color in chunks:
#             self.__gradient.setColorAt(passedWeight, color)
#             self.__gradient.setColorAt(passedWeight + weight - 0.0000000001, color)
#             passedWeight += weight
#         self.__gradient.setCenter(QPoint(0, 0))
#         self.__gradient.setAngle(-90)
#         self.update()
#     def paintEvent(self, event: QPaintEvent) ->None:
#         super().paintEvent(event)
#         drawSize = min(self.width() / 2, self.height())
#         painter = QPainter(self)
#         painter.drawRect(QRect(1, 1, self.width() - 2, self.height() - 2))
#         # first value
#         painter.setBrush(QColor('#ebbf58'))
#         painter.drawRect((self.width() / 2) - 30, 10, 50, 30)
#         value1 = str(round(self.__value1, 1))
#         painter.drawText((self.width() / 2) - 25, 30, value1)
#         # satellite label
#         satellite_label = "Сателит"
#         painter.setPen(QColor('black'))
#         painter.drawText((self.width() / 2) + 150, 30, satellite_label)
#         # satellite value
#         painter.setBrush(QColor('black'))
#         painter.drawRect(self.width() - (self.width() / 10) - 20, 10, 50, 30)
#         value2 = str(round(self.__value2, 1))
#         painter.setPen(QColor('white'))
#         painter.drawText(self.width() - (self.width() / 10) - 15, 30, value2)
#         painter.setRenderHint(QPainter.Antialiasing, True)
#         painter.setPen(QPen(Qt.black, 2, Qt.SolidLine))
#         painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
#         if self.state_button_1:
#             painter.setBrush(QBrush(QColor(self.color_green)))
#         else:
#             painter.setBrush(QBrush(QColor(self.color_red)))
#         painter.drawEllipse(50, 50, 20, 20)
#         if self.state_button_2:
#             painter.setBrush(QBrush(QColor(self.color_green)))
#         else:
#             painter.setBrush(QBrush(QColor(self.color_red)))
#         painter.drawEllipse(30, 70, 20, 20)
#         if self.state_button_3:
#             painter.setBrush(QBrush(QColor(self.color_green)))
#         else:
#             painter.setBrush(QBrush(QColor(self.color_red)))
#         painter.drawEllipse(70, 70, 20, 20)
#         painter.translate(self.width() / 2, self.height())
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         self.__drawColorArc(drawSize, painter)
#         self.__drawArrowPointer(drawSize, painter)
#         painter.end()
#
#     def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
#         painter.save()
#         path = QPainterPath()
#         path.addEllipse(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
#         painter.setBrush(QBrush(self.__gradient))
#         drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
#         painter.drawChord(drawingRect, 0, 180 * 16)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         painter.restore()
#
#     def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
#         painter.save()
#         painter.setBrush(self.__arrowColor)
#         painter.scale(drawSize / 100.0, drawSize / 100.0)
#         painter.rotate(float(numpy.interp(self.__value1, self.valueRange(), (-90, 90))))
#         painter.drawConvexPolygon(self.__arrow)
#         painter.restore()
#

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





