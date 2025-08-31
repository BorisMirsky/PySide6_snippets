import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *


class MyWindow(QWidget):
    def __init__(self, *args):
        QWidget.__init__(self, *args)
 
        # create table
        table = FreezeTableWidget(self)
 
        # layout
        layout = QVBoxLayout()
        layout.addWidget(table)
        self.setLayout(layout)
 
 
class FreezeTableWidget(QTableView):
    def __init__(self, parent = None, *args):
        QTableView.__init__(self, parent, *args)
 
        # Минимальный размер окна
        self.setMinimumSize(800, 600)
 
        # set the table model
        tm = MyTableModel(self)
 
        # set the proxy model
        pm = QSortFilterProxyModel(self)
        pm.setSourceModel(tm)
 
        # назначаем модель данных для TableView
        self.setModel(pm)
 
        # ***ВИДЖЕТ ЗАФИКСИРОВАННЫХ СТОЛБЦОВ***
        #  (будет расположен поверх основного)
        self.frozenTableView = QTableView(self)
        # устанавливаем модель для виджета зафиксированных столбцов
        self.frozenTableView.setModel(pm)
        # скрываем заголовки строк
        self.frozenTableView.verticalHeader().hide()
        # виджет не принимает фокус
        self.frozenTableView.setFocusPolicy(Qt.NoFocus)
        # пользователь не может изменять размер столбцов
        self.frozenTableView.horizontalHeader().ResizeMode(QHeaderView.Fixed)   #setResizeMode
        # отключаем показ границ виджета
        self.frozenTableView.setStyleSheet('''border: none; background-color: #8EDE21; 
                                       selection-background-color: #999''')
        # режим выделения как у основного виджета
        self.frozenTableView.setSelectionModel(QAbstractItemView.selectionModel(self))
        # убираем полосы прокрутки
        self.frozenTableView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozenTableView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
 
        # помещает дополнительный виджет на передний план
        self.viewport().stackUnder(self.frozenTableView)
 
        # Вход в режим редактирования - еще одним щелчком мыши
        self.setEditTriggers(QAbstractItemView.SelectedClicked)
 
        # hide gridnt()
#        self.setShowGrid(False)
 
        # Установка шрифта
        self.setStyleSheet('font: 10pt "Courier New"')
 
        # Установка свойств заголовков столбцов
        hh = self.horizontalHeader()
        # выравнивание текста по центру
        hh.setDefaultAlignment(Qt.AlignCenter)
        # включаем растягивание последнего столбца
        hh.setStretchLastSection(True)
 
        # Установка ширины столбцов по содержимому
#        self.resizeColumnsToContents()
 
        # Установка ширины столбцов
        ncol = tm.columnCount(self)
        for col in range(ncol):
            if col == 0:
                # устанавливаем размер
                self.horizontalHeader().resizeSection(col, 60)
                # фиксируем ширину
            #    self.horizontalHeader().ResizeMode(col, QHeaderView.Fixed)  #setResizeMode
                # ширина фиксированных столбцов - как у основного виджета
                self.frozenTableView.setColumnWidth(col, self.columnWidth(col))
            elif col == 1:
                self.horizontalHeader().resizeSection(col, 150)
           #     self.horizontalHeader().setResizeMode(col, QHeaderView.Fixed)
                self.frozenTableView.setColumnWidth(col, self.columnWidth(col))
            else:
                self.horizontalHeader().resizeSection(col, 100)
                # скрываем не нужные столбцы у виджета зафиксированных столбцов
                self.frozenTableView.setColumnHidden(col, True)
 
        # Сортировка по щелчку на заголовке столбца
        self.frozenTableView.setSortingEnabled(True)
        self.frozenTableView.sortByColumn(0, Qt.AscendingOrder)
 
        # Включаем чередующуюся подсветку строк
        self.setAlternatingRowColors(True)
 
        # Установка свойств заголовков строк
        vh = self.verticalHeader()
        vh.setDefaultSectionSize(25) # высота строк
        vh.setDefaultAlignment(Qt.AlignCenter) # выравнивание текста по центру
        vh.setVisible(True)
        # высота строк - как у основного виджета
        self.frozenTableView.verticalHeader().setDefaultSectionSize(vh.defaultSectionSize())
 
        # Альтернативная устновка высоты строк
#        nrows = tm.rowCount(self)
#        for row in xrange(nrows):
#            self.setRowHeight(row, 25)
 
        # показываем наш дополнительный виджет
        self.frozenTableView.show()
        # устанавливаем ему размеры как у основного
        self.updateFrozenTableGeometry()
 
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.frozenTableView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
 
        # Создаем соединения
        tm.dataChanged.connect(self.test)
        # connect the headers and scrollbars of both tableviews together
        self.horizontalHeader().sectionResized.connect(self.updateSectionWidth)
        self.verticalHeader().sectionResized.connect(self.updateSectionHeight)
        self.frozenTableView.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(self.frozenTableView.verticalScrollBar().setValue)
 
    def test(self, index):
        print(index.row(), index.column())
 
    def updateSectionWidth(self, logicalIndex, oldSize, newSize):
        if logicalIndex==0 or logicalIndex==1:
            self.frozenTableView.setColumnWidth(logicalIndex, newSize)
            self.updateFrozenTableGeometry()
 
    def updateSectionHeight(self, logicalIndex, oldSize, newSize):
        self.frozenTableView.setRowHeight(logicalIndex, newSize)
 
    def resizeEvent(self, event):
        QTableView.resizeEvent(self, event)
        self.updateFrozenTableGeometry()
 
    def scrollTo(self, index, hint):
        if index.column() > 1:
            QTableView.scrollTo(self, index, hint)
 
    def updateFrozenTableGeometry(self):
        if self.verticalHeader().isVisible():
            self.frozenTableView.setGeometry(self.verticalHeader().width() + self.frameWidth(),
                         self.frameWidth(), self.columnWidth(0) + self.columnWidth(1),
                         self.viewport().height() + self.horizontalHeader().height())
        else:
            self.frozenTableView.setGeometry(self.frameWidth(),
                         self.frameWidth(), self.columnWidth(0) + self.columnWidth(1),
                         self.viewport().height() + self.horizontalHeader().height())
 
    # переопределяем функцию moveCursor, для корректного скрола влево с клавиатуры
    def moveCursor(self, cursorAction, modifiers):
        current = QTableView.moveCursor(self, cursorAction, modifiers)
        if cursorAction == self.MoveLeft and current.column() > 1 and self.visualRect(current).topLeft().x() < (self.frozenTableView.columnWidth(0) + self.frozenTableView.columnWidth(1)):
            newValue = self.horizontalScrollBar().value() + self.visualRect(current).topLeft().x() - (self.frozenTableView.columnWidth(0) + self.frozenTableView.columnWidth(1))
            self.horizontalScrollBar().setValue(newValue)
        return current
 
 
class MyTableModel(QAbstractTableModel):
    def __init__(self, parent = None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.colLabels = ['Col1', 'Col2', 'Col3', 'Col4', 'Col5', 'Col6',
                          'Col7', 'Col8', 'Col9', 'Col10'] # Заголовки столбцов
        self.dataCached = [
                        [111, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
                        [112, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
                        [113, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
                        [114, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
                        [115, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
                        [116, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
                        [117, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
                        [118, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
                        [119, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
                        [120, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
                        [121, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
                        [122, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
                        [123, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
                        [124, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
                        [125, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
                        [126, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
                        [127, 'cell12', 'cell13', 'cell14', 'cell15', 'cell12', 'cell13', 'cell14', 'cell15', 'cell16'],
                        [128, 'cell22', 'cell23', 'cell24', 'cell25', 'cell26', 'cell27', 'cell28', 'cell29', 'cell30'],
                        [129, 'cell32', 'cell33', 'cell34', 'cell35', 'cell36', 'cell37', 'cell38', 'cell39', 'cell40'],
                        [130, 'cell42', 'cell43', 'cell44', 'cell45', 'cell46', 'cell47', 'cell48', 'cell49', 'cell50'],
                        [131, 'cell52', 'cell53', 'cell54', 'cell55', 'cell56', 'cell57', 'cell58', 'cell59', 'cell60'],
                        [132, 'cell62', 'cell63', 'cell64', 'cell65', 'cell66', 'cell67', 'cell68', 'cell69', 'cell70'],
                        [133, 'cell72', 'cell73', 'cell74', 'cell75', 'cell76', 'cell77', 'cell78', 'cell79', 'cell80'],
                        [134, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
                        [135, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90'],
                        [136, 'cell82', 'cell83', 'cell84', 'cell85', 'cell86', 'cell87', 'cell88', 'cell89', 'cell90']
                    ] # Область данных
 
    # Возвращает количество строк
    def rowCount(self, parent):
        return len(self.dataCached)
 
    # Возвращает количество столбцов
    def columnCount(self, parent):
        return len(self.colLabels)
 
    # Возвращает значение ячейки
    def get_value(self, index):
        i = index.row()
        j = index.column()
        return self.dataCached[i][j]
 
    # Значение и свойства ячейки данных в зависимости от роли
    def data(self, index, role):
        if not index.isValid():
            return None
        value = self.get_value(index)
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return value
        elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter
        return None
 
    # Изменение значения ячейки
    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            self.dataCached[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False
 
    # Заголовки столбцов и строк
    def headerData(self, section, orientation, role):
        #заголовки столбцов
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            header = self.colLabels[section]
            return header
        #заголовки строк
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)
 
        return None
 
    # Переопределяем метод flags (включаем выделение и редактирование в ячейках)
    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        elif index.column() > 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
 
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
 
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec())
 
