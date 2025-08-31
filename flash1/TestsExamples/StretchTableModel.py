import sys
from PySide6 import QtWidgets
from PySide6.QtCore import QAbstractTableModel, Qt



class TableModel(QAbstractTableModel):
    def __init__(self, parent, datain, headerdata):
        QAbstractTableModel.__init__(self, parent)
        self.arraydata=datain
        self.headerdata=headerdata

    def rowCount(self,p):
        return len(self.arraydata)

    def columnCount(self,p):
        if len(self.arraydata)>0:
            return len(self.arraydata[0])
        return 0

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        else:
            if role == Qt.DisplayRole or role == Qt.EditRole:
                return str(self.arraydata[index.row()][index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation==Qt.Horizontal and role==Qt.DisplayRole:
            return self.headerdata[col]
        return None



class MyHeaderView(QtWidgets.QHeaderView):
    def __init__(self,parent):
        QtWidgets.QHeaderView.__init__(self,Qt.Horizontal,parent)
        self.sectionResized.connect(self.myresize)

    def myresize(self, *args):
        ws=[]
        for c in range(self.count()):
            wii=self.sectionSize(c)
            ws.append(wii)

        if args[0]>0 or args[0]<self.count():
            for ii in range(args[0],self.count()):
                if ii==args[0]:
                    self.resizeSection(ii,args[2])
                elif ii==args[0]+1:
                    self.resizeSection(ii,ws[ii]-(args[2]-args[1]))
                else:
                    self.resizeSection(ii,ws[ii])

    def resizeEvent(self, event):
        super(QtWidgets.QHeaderView, self).resizeEvent(event)
        self.setSectionResizeMode(1,QtWidgets.QHeaderView.Stretch)
        for column in range(self.count()):
            self.setSectionResizeMode(column, QtWidgets.QHeaderView.Stretch)
            width = self.sectionSize(column)
            print(width)
            self.setSectionResizeMode(column, QtWidgets.QHeaderView.Interactive)
            self.resizeSection(column, width)
        return


class MainFrame(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainFrame,self).__init__()
        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        self.doc_table = self.createTable()
        box = QtWidgets.QGroupBox("Table")
        h_layout = QtWidgets.QHBoxLayout(box)
        h_layout.addWidget(self.doc_table)
        g_layout = QtWidgets.QGridLayout(self.centralWidget)
        g_layout.addWidget(box, 1, 1)
        self.show()

    def createTable(self):
        self.tabledata=[['aaa' ,' title1', True, 1999],
                    ['bbb' ,' title2', True, 2000],
                    ['ccc' ,' title3', False, 2001]
                    ]
        header=['author', 'title', 'read', 'year']
        tablemodel=TableModel(self,self.tabledata,header)
        tv=QtWidgets.QTableView(self)
        hh=MyHeaderView(self)
        tv.setHorizontalHeader(hh)
        tv.setModel(tablemodel)
        tv.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        tv.setShowGrid(True)
        hh.setSectionsMovable(True)
        hh.setStretchLastSection(False)
        return tv


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.main_frame=MainFrame()
        self.setCentralWidget(self.main_frame)
        self.setGeometry(100,100,800,600)
        self.show()


if __name__=='__main__':
    app=QtWidgets.QApplication(sys.argv)
    mainwindow=MainWindow()
    sys.exit(app.exec())