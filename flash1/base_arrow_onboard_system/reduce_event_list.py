from domain.models.QTableModelDelayEventsAdapter import QTableModelDelayEventsAdapter
import PySide6.QtWidgets as QtWidgets
import PySide6.QtCore as QtCore
import PySide6.QtGui as QtGui
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    model = QtGui.QStandardItemModel(0, 3)
    model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, 'v1')
    model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, 'v2')
    model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, 'v3')
    model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, 'v4')
    model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, 'v5')
    model_adapter = QTableModelDelayEventsAdapter(table = model)
    
    
    
    def append_row_to_table():
        append_row_to_table.current_row_index += 1
        model.appendRow([
            QtGui.QStandardItem(f'r-{append_row_to_table.current_row_index}-c-0'),
            QtGui.QStandardItem(f'r-{append_row_to_table.current_row_index}-c-1'),
            QtGui.QStandardItem(f'r-{append_row_to_table.current_row_index}-c-2'),
            QtGui.QStandardItem(f'r-{append_row_to_table.current_row_index}-c-3'),
            QtGui.QStandardItem(f'r-{append_row_to_table.current_row_index}-c-4'),
        ])
        
    append_row_to_table.current_row_index = 0
    append_row_to_table_timer = QtCore.QTimer()
    append_row_to_table_timer.timeout.connect(append_row_to_table)
    append_row_to_table_timer.start(500)
    
    view = QtWidgets.QTableView()
    view.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
    view.setModel(model_adapter)
    view.show()
    sys.exit(app.exec())