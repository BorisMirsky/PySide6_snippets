import PySide6.QtCore as QtCore
import dataclasses

class QTableModelDelayEventsAdapter(QtCore.QAbstractTableModel):
    @dataclasses.dataclass(frozen = True, slots = True)
    class ModelDataChangedEvent: 
        topLeft: QtCore.QModelIndex
        bottomRight: QtCore.QModelIndex
        roles: list[int]
    @dataclasses.dataclass(frozen = True, slots = True)
    class BeforeModelRowInsertEvent:
        parent: QtCore.QModelIndex
        start: int
        end: int
    @dataclasses.dataclass(frozen = True, slots = True)
    class AfterModelRowInsertEvent: 
        parent: QtCore.QModelIndex
        start: int
        end: int
    @dataclasses.dataclass(frozen = True, slots = True)
    class BeforeModelRowRemoveEvent: 
        parent: QtCore.QModelIndex
        start: int
        end: int
    @dataclasses.dataclass(frozen = True, slots = True)
    class AfterModelRowRemoveEvent: 
        parent: QtCore.QModelIndex
        start: int
        end: int
    @dataclasses.dataclass(frozen = True, slots = True)
    class BeforeModelResetEvent: 
        pass
    @dataclasses.dataclass(frozen = True, slots = True)
    class AfterModelResetEvent: 
        pass

    def __init__(self, table: QtCore.QAbstractTableModel, parent: QtCore.QObject | None = None) ->None:
        super().__init__(parent = parent)
        self.__table: QtCore.QAbstractTableModel = table
        self.__events_log: list = []
        
        self.__table.dataChanged.connect(lambda topLeft, bottomRight, roles: self.__events_log.append(QTableModelDelayEventsAdapter.ModelDataChangedEvent(topLeft, bottomRight, roles)))
        self.__table.rowsAboutToBeInserted.connect(lambda parent, start, end: self.__events_log.append(QTableModelDelayEventsAdapter.BeforeModelRowInsertEvent(parent, start, end)))
        self.__table.rowsInserted.connect(lambda parent, start, end: self.__events_log.append(QTableModelDelayEventsAdapter.AfterModelRowInsertEvent(parent, start, end)))
        self.__table.rowsAboutToBeRemoved.connect(lambda parent, start, end: self.__events_log.append(QTableModelDelayEventsAdapter.BeforeModelRowRemoveEvent(parent, start, end)))
        self.__table.rowsRemoved.connect(lambda parent, start, end: self.__events_log.append(QTableModelDelayEventsAdapter.AfterModelRowRemoveEvent(parent, start, end)))
        self.__table.modelAboutToBeReset.connect(lambda: self.__events_log.append(QTableModelDelayEventsAdapter.BeforeModelResetEvent()))
        self.__table.modelReset.connect(lambda: self.__events_log.append(QTableModelDelayEventsAdapter.AfterModelResetEvent()))
        
        self.__flushEventLogTimer = QtCore.QTimer(self)
        self.__flushEventLogTimer.timeout.connect(self.flushEventLogBuffer)
        self.__flushEventLogTimer.start(2000)
    def flags(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex) -> QtCore.Qt.ItemFlag:
        return self.__table.flags(self.__table.index(index.row(), index.column()))
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> any:
        return self.__table.headerData(section, orientation, role)
    def data(self, index: QtCore.QModelIndex | QtCore.QPersistentModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole) -> any:
        return self.__table.data(self.__table.index(index.row(), index.column()), role)
    def rowCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex = QtCore.QModelIndex()) -> int:
        return self.__table.rowCount(self.__table.index(parent.row(), parent.column()))
    def columnCount(self, parent: QtCore.QModelIndex | QtCore.QPersistentModelIndex = QtCore.QModelIndex) -> int:
        return self.__table.columnCount(self.__table.index(parent.row(), parent.column()))
    def flushEventLogBuffer(self) ->None:
        current_events, self.__events_log = self.__events_log, []
        for event in current_events:
            # print(f'[Handle event][{event}]')
            match type(event):
                case QTableModelDelayEventsAdapter.ModelDataChangedEvent:
                    self.dataChanged.emit(self.index(event.topLeft.row(), event.topLeft.column()), self.index(event.bottomRight.row(), event.bottomRight.column()), event.roles)
                case QTableModelDelayEventsAdapter.BeforeModelRowInsertEvent:
                    self.beginInsertRows(QtCore.QModelIndex(), event.start, event.end)
                case QTableModelDelayEventsAdapter.AfterModelRowInsertEvent:
                    self.endInsertRows()
                case QTableModelDelayEventsAdapter.BeforeModelRowRemoveEvent:
                    self.beginRemoveRows(QtCore.QModelIndex(), event.start, event.end)
                case QTableModelDelayEventsAdapter.AfterModelRowRemoveEvent:
                    self.endRemoveRows()
                case QTableModelDelayEventsAdapter.BeforeModelResetEvent:
                    self.beginResetModel()
                case QTableModelDelayEventsAdapter.AfterModelResetEvent:
                    self.endResetModel()
                case (_):
                    pass
