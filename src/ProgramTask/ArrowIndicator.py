# This Python file uses the following encoding: utf-8
from PySide6.QtGui import (QPainter, QColor, QPolygon, QPen, QPaintEvent,
                           QConicalGradient, QGradient, QBrush, QRegion, QResizeEvent, QPainterPath)
from PySide6.QtCore import Signal, QSize, QRect, QPoint, Qt
from PySide6.QtWidgets import QWidget, QSizePolicy, QLabel
from typing import List, Tuple
import numpy


class ArrowPointerIndicator(QWidget):

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
        self.__value: float = 0.0

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
        painter.translate(self.width() / 2, self.height())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.__drawColorArc(drawSize, painter)
        self.__drawArrowPointer(drawSize, painter)

    def __drawColorArc(self, drawSize: int, painter: QPainter) ->None:
        # drawingRect = QRect(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        # excludeRect = QRect(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth, 2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        # painter.save()
        # outerRegion = QRegion(drawingRect, QRegion.RegionType.Ellipse).subtracted(QRegion(excludeRect, QRegion.RegionType.Ellipse))
        # painter.setClipRegion(outerRegion)
        # painter.setBrush(QBrush(self.__gradient))
        # painter.drawChord(drawingRect, 0, 180 * 16)
        # painter.restore()
        painter.save()
        path = QPainterPath()
        path.addEllipse(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize)
        path.addEllipse(-drawSize + self.__lineWidth, -drawSize + self.__lineWidth,
                        2 * (drawSize - self.__lineWidth), 2 * (drawSize - self.__lineWidth))
        painter.setClipPath(path)
        painter.setBrush(QBrush(self.__gradient))
        painter.drawChord(-drawSize, -drawSize, 2 * drawSize, 2 * drawSize, 0, 180 * 16)
        painter.restore()

    def __drawArrowPointer(self, drawSize: int, painter: QPainter) ->None:
        painter.save()
        painter.setBrush(self.__arrowColor)
        painter.scale(drawSize / 100.0, drawSize / 100.0)
        painter.drawConvexPolygon(self.__arrow)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.restore()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ArrowPointerIndicator(
            chunks=[
                (4, Qt.GlobalColor.white),
                (1, Qt.GlobalColor.red),
                (1, Qt.GlobalColor.white),
                (1, Qt.GlobalColor.red),
                (4, Qt.GlobalColor.white),
        ], lineWidth=1000000)
    window.show()
    sys.exit(app.exec())


