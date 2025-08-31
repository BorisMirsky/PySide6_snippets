from PySide6.QtWidgets import QWidget, QApplication, QVBoxLayout, QStackedLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal, Slot



class Outer(QWidget):
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.resize(500,300)
        self.stackedLayout = QStackedLayout()
        self.inner1 = InnerClass1()
        self.inner2 = InnerClass2()
        self.inner1.signalChangeLayout1.connect(self.change_layout_1_to_2)
        self.inner2.signalChangeLayout2.connect(self.change_layout_2_to_1)
        self.stackedLayout.addWidget(self.inner1)
        self.stackedLayout.addWidget(self.inner2)
        self.setLayout(self.stackedLayout)

    def change_layout_1_to_2(self):
        self.setWindowTitle("InnerClass 2")
        self.stackedLayout.setCurrentIndex(1)

    def change_layout_2_to_1(self):
        self.setWindowTitle("InnerClass 1")
        self.stackedLayout.setCurrentIndex(0)



class InnerClass1(QWidget):
    signalChangeLayout1 = Signal(str)
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        #self.setWindowTitle("InnerClass 1")
        lbl = QLabel("Это класс 1")
        btn = QPushButton("")
        btn.clicked.connect(self.runChangeLayout1)
        vbox = QVBoxLayout()
        vbox.addWidget(lbl)
        vbox.addWidget(btn)
        self.setLayout(vbox)

    def runChangeLayout1(self):
        self.signalChangeLayout1.emit("go!")


class InnerClass2(QWidget):
    signalChangeLayout2 = Signal(str)
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        #self.setWindowTitle("InnerClass 2")
        lbl = QLabel("Это класс 2")
        btn = QPushButton("")
        btn.clicked.connect(self.runChangeLayout2)
        vbox = QVBoxLayout()
        vbox.addWidget(btn)
        vbox.addWidget(lbl)
        self.setLayout(vbox)

    def runChangeLayout2(self):
        self.signalChangeLayout2.emit("go!")


if __name__ == '__main__':
    app = QApplication()
    win = Outer()
    win.show()
    app.exec()
