# This Python file uses the following encoding: utf-8
from domain.dto.Markers import RailwayMarker, RailwayMarkerLocation, RailwayMarkerType
from domain.dto.Travelling import LocationVector1D, PicketDirection, MovingDirection
from domain.units.AbstractUnit import AbstractReadUnit
from domain.markers.BaseRailwayMarkerModel import BaseRailwayMarkerModel
from domain.markers.AbstractMarkerModel import AbstractMarkerModel
from presentation.ui.gui.common.viewes.TableDataChartsView import DynamicLineSeries
from presentation.ui.gui.common.elements.SingleLineModel import SingleLineModel
from PySide6.QtCore import (
    Signal, QTimer, QObject, QModelIndex, QPersistentModelIndex, QIdentityProxyModel, QCoreApplication
)
from PySide6.QtCharts import QScatterSeries, QLineSeries, QVXYModelMapper, QChart, QChartView, QBarCategoryAxis, QValueAxis, QLegend
from PySide6.QtGui import QFont, QIcon, QShortcut, QKeySequence, Qt, QPen, QPainter, QImage, QPixmap, QColor, QBrush
from PySide6.QtWidgets import (
    QWidget, QLabel, QListWidget, QListWidgetItem, QVBoxLayout,
)
from typing import Optional, Union, Tuple, Any, List

QCoreApplication.translate('Measurement/control units', 'left')
QCoreApplication.translate('Measurement/control units', 'middle')
QCoreApplication.translate('Measurement/control units', 'right')
QCoreApplication.translate('Measurement/control units', 'position')   # added



# класс выбора маркеров пути
class SelectCurrentMarkerWindow(QWidget):
    ITEM_RAILWAY_MODEL_ROLE: int = Qt.ItemDataRole.UserRole + 2001
    ITEM_RAILWAY_MARKER_ROLE: int = Qt.ItemDataRole.UserRole + 2002
    ITEM_IS_CONTINUATION_ROLE: int = Qt.ItemDataRole.UserRole + 2003
    def __init__(self, position_unit: AbstractReadUnit[float], marker_step: float, railway_markers: List[Tuple[AbstractMarkerModel, RailwayMarker, QIcon, bool]], parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__position_unit: AbstractReadUnit[float] = position_unit
        self.__position_unit.changed.connect(self.__process_current_marker)
        self.__current_continuation_maker: Tuple[AbstractMarkerModel, RailwayMarker] = None
        self.__old_process_position: float = None
        self.__marker_step: float = marker_step

        self.__railway_marker_list_view = QListWidget()
        self.__railway_marker_list_view.itemActivated.connect(self.__railway_item_selected)
        self.__railway_marker_list_view.addItem(QListWidgetItem(QCoreApplication.translate('Environment/Railway/Markers', 'Clear')))
        for railway_model, railway_marker, icon, is_continuation in railway_markers:
            marker_item = QListWidgetItem(icon, QCoreApplication.translate('Environment/Railway/Markers', railway_marker.title))
            marker_item.setData(SelectCurrentMarkerWindow.ITEM_RAILWAY_MODEL_ROLE, railway_model)
            marker_item.setData(SelectCurrentMarkerWindow.ITEM_RAILWAY_MARKER_ROLE, railway_marker)
            marker_item.setData(SelectCurrentMarkerWindow.ITEM_IS_CONTINUATION_ROLE, is_continuation)
            self.__railway_marker_list_view.addItem(marker_item)

        self.__close_window_shortcut = QShortcut(QKeySequence.StandardKey.Cancel, self)
        self.__close_window_shortcut.activated.connect(self.hide)

        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel('Select marker'))
        layout.addWidget(self.__railway_marker_list_view)

        self.setWindowFlags(Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        

    def __process_current_marker(self, position) ->None:
        if self.__current_continuation_maker is None:
            return
        if self.__old_process_position is not None and abs(self.__old_process_position - position) < self.__marker_step:
            return
        
        self.__current_continuation_maker[0].insertMarkerAtPosition(self.__current_continuation_maker[1], LocationVector1D(meters = self.__position_unit.read()))
        self.__old_process_position = position
    def __reset_continuation_marker(self, marker: Tuple[AbstractMarkerModel, RailwayMarker] = None) ->None:
        self.__current_continuation_maker = marker
        self.__old_process_position = None
    def __railway_item_selected(self, item: QListWidgetItem) ->None:
        self.__reset_continuation_marker()
        railway_marker = item.data(SelectCurrentMarkerWindow.ITEM_RAILWAY_MARKER_ROLE)
        railway_model = item.data(SelectCurrentMarkerWindow.ITEM_RAILWAY_MODEL_ROLE)
        if railway_marker is None or railway_model is None:
            return

        railway_model.insertMarkerAtPosition(railway_marker, LocationVector1D(meters = self.__position_unit.read()))
        if item.data(SelectCurrentMarkerWindow.ITEM_IS_CONTINUATION_ROLE):
            self.__reset_continuation_marker((railway_model, railway_marker))

# класс маркеров пути
class SelectCurrentMarker(QWidget):
    ITEM_RAILWAY_MODEL_ROLE: int = Qt.ItemDataRole.UserRole + 2001
    ITEM_RAILWAY_MARKER_ROLE: int = Qt.ItemDataRole.UserRole + 2002
    ITEM_IS_CONTINUATION_ROLE: int = Qt.ItemDataRole.UserRole + 2003
    def __init__(self, position_unit: AbstractReadUnit[float], marker_step: float, parent: Optional[QWidget] = None) ->None:
        super().__init__(parent)
        self.__position_unit: AbstractReadUnit[float] = position_unit
        self.__position_unit.changed.connect(self.__process_current_marker)
        self.__current_continuation_maker: Tuple[AbstractMarkerModel, RailwayMarker] = None
        self.__old_process_position: float = None
        self.__marker_step: float = marker_step
        self.__is_continuation: bool = False

    def __process_current_marker(self, position) ->None:
        if self.__current_continuation_maker is None:
            return
        if self.__old_process_position is not None and abs(self.__old_process_position - position) < self.__marker_step:
            return
        
        self.__current_continuation_maker[0].insertMarkerAtPosition(self.__current_continuation_maker[1], LocationVector1D(meters = self.__position_unit.read()))
        self.__old_process_position = position
    def __reset_continuation_marker(self, marker: Tuple[AbstractMarkerModel, RailwayMarker] = None) ->None:
        self.__current_continuation_maker = marker
        self.__old_process_position = None
    def marker_selected(self, marker) ->None:
        self.__reset_continuation_marker()
        railway_model, railway_marker, icon, is_continuation = marker

        if railway_marker is None or railway_model is None:
            return

        railway_model.insertMarkerAtPosition(railway_marker, LocationVector1D(meters = self.__position_unit.read()))
        
        if is_continuation:
            self.__is_continuation = not self.__is_continuation
            if self.__is_continuation:
                self.__reset_continuation_marker((railway_model, railway_marker))
        else: self.__is_continuation = False

# ?
class RailwayMarkerTypeToLocationModel(QIdentityProxyModel):
    def __init__(self, origin: AbstractMarkerModel, parent: Optional[QObject] = None) ->None:
        super().__init__(parent = parent)
        self.setSourceModel(origin)
        self.__location_to_category: Dict[RailwayMarkerLocation, int] = {
            RailwayMarkerLocation.Left: 0,
            RailwayMarkerLocation.Middle: 1,
            RailwayMarkerLocation.Right: 2
        }
    def data(self, index: Union[QModelIndex, QPersistentModelIndex], role: int = Qt.ItemDataRole.DisplayRole) ->Any:
        if not index.isValid():
            return None
        data = super().data(index, role)
        if index.column() == 3 and role == Qt.ItemDataRole.DisplayRole:
            data = self.__location_to_category[data]
        return data

# класс графика
class RailwayMarkerLinesScatter(QChartView):
    # default Y max value for position chart
    y_axis_scale = 10
    options = None
    def __init__(
            self, position_unit: AbstractReadUnit[float], 
            position_window: Tuple[float, float], 
            railway_marker_models: List[Tuple[AbstractMarkerModel, QImage]], 
            parent: Optional[QWidget] = None,
            options=None
        ) ->None:
        super().__init__(chart = QChart(), parent = parent)
        self.setRenderHint(QPainter.Antialiasing)
        # хранит параметры окна измерительной поездки перед началом
        self.options = options
        self.__position_window: Tuple[float, float] = position_window
        self.__position_unit: AbstractReadUnit[float] = position_unit
        self.__position_unit.changed.connect(self.__on_position_changed)
        self.__railway_marker_models: List[Tuple[AbstractMarkerModel, QImage]] = [(RailwayMarkerTypeToLocationModel(model), image) for model, image in railway_marker_models]
        self.__railway_marker_scatter_series: List[QScatterSeries] = []
        self.__railway_marker_scatter_mapper: List[QVXYModelMapper] = []
        #
        self.chart().legend().setVisible(True)
        self.chart().legend().setLabelColor(QColor('white'))

        self.__category_axis = QBarCategoryAxis()
        self.__position_axis = QValueAxis()
        self.__position_axis.setRange(0, 1000)
        self.__category_axis.setCategories(['&lt', '*', '&gt'])
        self.__category_axis.setRange('left', 'right')
        self.chart().setAxisX(self.__category_axis)
        self.chart().setAxisY(self.__position_axis)
        self.chart().axisX().setGridLineVisible(False)
        self.chart().axisY().setGridLineVisible(False)

        rw_line_pen = QPen(QColor("white"))
        rw_line_pen.setWidth(2)
        rw_line_pen.setStyle(Qt.SolidLine)
        self.railway_line_series = QLineSeries()
        self.railway_line_series.setPen(rw_line_pen)
        self.chart().addSeries(self.railway_line_series)
        self.railway_line_series.attachAxis(self.__position_axis)
        self.railway_line_series.attachAxis(self.__category_axis)

        self.__on_position_changed(self.__position_unit.read())

        self.__position_unit_line_model = SingleLineModel(self.__position_unit.read())
        self.__position_unit.changed.connect(self.__position_unit_line_model.setPosition)
        self.__position_unit_line_series = DynamicLineSeries(self.__position_unit_line_model, 1, 0, 'Позиция', self)
        self.__position_unit_line_series.setName('Позиция')

        self.chart().addSeries(self.__position_unit_line_series)
        self.__position_unit_line_series.attachAxis(self.__position_axis)
        self.__position_unit_line_series.attachAxis(self.__category_axis)

        self.chart().setBackgroundBrush(QBrush("black"))
        axis_brush = QBrush(QColor("white"))
        self.__category_axis.setLabelsBrush(axis_brush)
        self.__position_axis.setLabelsBrush(axis_brush)

        
        self.__update_infinite_railway_line()
    
        for railway_marker_model, railway_marker_image in self.__railway_marker_models:
            series = QScatterSeries()
            mapper = QVXYModelMapper()
            mapper.setSeries(series)
            mapper.setModel(railway_marker_model)
            mapper.setXColumn(3)
            mapper.setYColumn(0)
            
            self.chart().addSeries(series)
            series.attachAxis(self.__category_axis)
            series.attachAxis(self.__position_axis)

            series.setPen(QColor(Qt.transparent))
            series.setBrush(railway_marker_image)
            series.setMarkerSize(32)

            self.__railway_marker_scatter_series.append(series)
            self.__railway_marker_scatter_mapper.append(mapper)
        # удаляем из легенды всё кроме "Позиции"
        legend = self.chart().legend()
        for marker in legend.markers():
            if marker.label() != 'Позиция':
                marker.setVisible(False)

        # Против пикетажа - движение вперед. Позиция приходти с минус знак, инвертируем ось Y, чтобы график строился снизу вверх
        if (
            self.options.moving_direction == MovingDirection.Forward 
            and 
            self.options.picket_direction == PicketDirection.Backward
        ):
            self.__position_axis.setReverse(
                True
            )
        
        if (
            self.options.moving_direction == MovingDirection.Backward 
            and 
            self.options.picket_direction == PicketDirection.Forward
        ):
            self.__position_axis.setReverse(
                True
            )

    def __update_infinite_railway_line(self):
        """ Обновляет линию '*' при изменении масштаба или позиции """
        self.railway_line_series.clear()

        categories = self.__category_axis.categories()
        middle_pos_index = (
            categories.index('&lt') + categories.index('&gt')
        ) / 2 or 1.5

        y_min = self.__position_axis.min()
        y_max = self.__position_axis.max()

        self.railway_line_series.append(middle_pos_index, y_min)
        self.railway_line_series.append(middle_pos_index, y_max)

    def __on_position_changed(self, position: float) -> None:
        """
            При смене позиции,  меняем масштаб оси Y
            только графика Позиции
        """
        
        if (
            self.options.picket_direction == PicketDirection.Forward and 
            self.options.moving_direction == MovingDirection.Forward
        ) or (
            self.options.picket_direction == PicketDirection.Forward and 
            self.options.moving_direction == MovingDirection.Backward
        ):
            max_pos = max(self.y_axis_scale + self.options.start_picket.meters, position)
            min_pos = max(
                self.options.start_picket.meters, max_pos - self.y_axis_scale
            )

        if (
            self.options.picket_direction == PicketDirection.Backward and 
            self.options.moving_direction == MovingDirection.Forward
        ) or (
            self.options.picket_direction == PicketDirection.Backward and 
            self.options.moving_direction == MovingDirection.Backward
        ):
            threshold = self.options.start_picket.meters - self.y_axis_scale
            if position > threshold:
                max_pos = self.options.start_picket.meters
            else:
                max_pos = max(position + self.y_axis_scale, position)
            
            min_pos = min(max_pos - self.y_axis_scale, position)

        self.chart().axisY().setRange(
            min_pos, max_pos
        )
        self.__update_infinite_railway_line()

    def scale_change(
        self, scale: int
    ):
        """
            Обновить масштаб из MeasureView combo box
        """
        self.y_axis_scale = scale
