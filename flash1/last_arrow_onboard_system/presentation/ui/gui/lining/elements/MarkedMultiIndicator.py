# This Python file uses the following encoding: utf-8
from domain.units.AbstractUnit import AbstractReadUnit
from PySide6.QtWidgets import QProgressBar, QSlider, QBoxLayout, QWidget
from PySide6.QtCore import QPointF, QLineF, QRectF, Qt
from PySide6.QtGui import QPainter
from typing import List, Tuple, Optional
import numpy

class IndicatorMarking(QWidget):
    def __init__(self, orientation: Qt.Orientation, max_value: int, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.setMinimumSize(40, 40)
        self.__orientation: Qt.Orientation = orientation
        self.__max_value: int = max_value

    def paintEvent(self, event) ->None:
        super().paintEvent(event)

        painter = QPainter(self)
        lines, labels = self.createDrawEntities()
        if self.__orientation == Qt.Orientation.Vertical:
            painter.translate(self.width(), self.height() / 2)
            painter.rotate(90)
        else:
            painter.translate(self.width() / 2, 0)

        painter.drawLines(lines)
        for label in labels:
            painter.drawText(label[0], Qt.AlignmentFlag.AlignCenter, label[1])

    def createDrawEntities(self) ->Tuple[List[QLineF], List[Tuple[QRectF, str]]]:
        sub_tick_line_split = 0.2 * (self.height() if self.__orientation == Qt.Orientation.Horizontal else self.width())
        tick_line_split = 2 * sub_tick_line_split
        tick_text_split = 5 * sub_tick_line_split
        marker_space_size = ((self.width() if self.__orientation == Qt.Orientation.Horizontal else self.height()) - 5) / (2 * self.__max_value)
        tick_text_size = marker_space_size / 2

        lines: List[QLineF] = []
        labels: List[Tuple[QRectF, str]] = []

        for element in range(0, self.__max_value + 1):
            tick_position = element * marker_space_size

            lines.append(QLineF(QPointF(-tick_position, 0), QPointF(-tick_position, tick_line_split)))
            lines.append(QLineF(QPointF(tick_position, 0), QPointF(tick_position, tick_line_split)))
            labels.append((QRectF(QPointF(-tick_position - tick_text_size, tick_line_split), QPointF(-tick_position + tick_text_size, tick_text_split)), str(-element)))
            labels.append((QRectF(QPointF(tick_position - tick_text_size, tick_line_split), QPointF(tick_position + tick_text_size, tick_text_split)), str(element)))

            tick_sub_line_size = marker_space_size / 5
            for sub_element in range(1, 5):
                sub_tick_position = sub_element * tick_sub_line_size
                lines.append(QLineF(QPointF(-sub_tick_position - tick_position, 0), QPointF(-sub_tick_position - tick_position, sub_tick_line_split)))
                lines.append(QLineF(QPointF(sub_tick_position + tick_position, 0), QPointF(sub_tick_position + tick_position, sub_tick_line_split)))

        return (lines, labels)

class DoubleSideFillIndicator(QWidget):
    def __init__(self, orientation: Qt.Orientation, max_value: float, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__negative_view: QProgressBar = QProgressBar()
        self.__positive_view: QProgressBar = QProgressBar()
        self.__negative_view.setProperty('class', 'double-side-indicator-slider')
        self.__positive_view.setProperty('class', 'double-side-indicator-slider')
        self.__negative_view.setInvertedAppearance(True)
        self.__negative_view.setOrientation(orientation)
        self.__positive_view.setOrientation(orientation)
        self.__negative_view.setRange(0, max_value)
        self.__positive_view.setRange(0, max_value)
        self.__negative_view.setTextVisible(False)
        self.__positive_view.setTextVisible(False)

        layout = QBoxLayout(self.qtOrientationToBoxLayoutDirection(orientation))
        layout.addWidget(self.__negative_view)
        layout.addWidget(self.__positive_view)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    @staticmethod
    def qtOrientationToBoxLayoutDirection(orientation: Qt.Orientation) ->QBoxLayout.Direction:
        match orientation:
            case Qt.Orientation.Horizontal:
                return QBoxLayout.Direction.LeftToRight
            case Qt.Orientation.Vertical:
                return QBoxLayout.Direction.BottomToTop
            case _:
                raise Exception('Invalid horizontal value')

    def setValue(self, value: float):
        self.__negative_view.setValue(numpy.clip(-value, self.__negative_view.minimum(), self.__negative_view.maximum()))
        self.__positive_view.setValue(numpy.clip(value, self.__positive_view.minimum(), self.__positive_view.maximum()))

class MarkerScrollIndicator(QSlider):
    def __init__(self, orientation: Qt.Orientation, max_value: float, parent: Optional[QWidget] = None) ->None:
        super().__init__(orientation, parent)
        self.setRange(-max_value, max_value)
        self.setEnabled(False)



class MarkedMultiIndicator(QWidget):
    def __init__(self, double_side_indicator_model: AbstractReadUnit[float], scroll_indicator_model: AbstractReadUnit[float], orientation: Qt.Orientation, max_value: float, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__double_side_indicator_model: AbstractReadUnit[float] = double_side_indicator_model
        self.__scroll_indicator_model: AbstractReadUnit[float] = scroll_indicator_model
        self.__double_side_indicator = DoubleSideFillIndicator(orientation, 100 * max_value)
        self.__scroll_indicator = MarkerScrollIndicator(orientation, 100 * max_value)
        self.__double_side_indicator_model.changed.connect(self.__double_side_indicator_model_changed)
        self.__scroll_indicator_model.changed.connect(self.__scroll_indicator_model_changed)

        self.__layout = QBoxLayout(self.qtOrientationToBoxLayoutDirection(orientation))
        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.addWidget(IndicatorMarking(orientation, max_value))
        self.__layout.addWidget(self.__double_side_indicator)
        self.__layout.addWidget(self.__scroll_indicator)
        self.setLayout(self.__layout)

    def __double_side_indicator_model_changed(self, value: float) ->None:
        self.__double_side_indicator.setValue(100 * (value or 0.0))
    def __scroll_indicator_model_changed(self, value: float) ->None:
        self.__scroll_indicator.setValue(100 * (value or 0.0))

    @staticmethod
    def qtOrientationToBoxLayoutDirection(orientation: Qt.Orientation) ->QBoxLayout.Direction:
        match orientation:
            case Qt.Orientation.Horizontal:
                return QBoxLayout.Direction.BottomToTop
            case Qt.Orientation.Vertical:
                return QBoxLayout.Direction.LeftToRight
            case _:
                raise Exception('Invalid horizontal value')

    def setValue(self, value: float):
        value *= 100
        self.__filling.setValue(value)
        self.__marker.setValue(value)




