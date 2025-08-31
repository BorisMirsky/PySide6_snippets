from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QPushButton, QStackedLayout, QLabel
import sys
from ..first.buttons import Buttons
from ..second.line_edit import  LineEdit


class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300,200)
        self.test_lbl = QLabel("MainView")
        self.value_lbl = QLabel()
        self.btn1 = QPushButton('btn1')
        #self.btn1.clicked.connect(lambda: self.handleBtn(1))
        self.btn1.clicked.connect(self.handleBtn1)
        self.btn2 = QPushButton('btn2')
        #self.btn2.clicked.connect(lambda: self.handleBtn(2))
        self.btn2.clicked.connect(self.handleBtn2)
        vbox = QVBoxLayout()
        vbox.addWidget(self.test_lbl)
        vbox.addWidget(self.value_lbl)
        vbox.addWidget(self.btn1)
        vbox.addWidget(self.btn2)
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(vbox)
        self.currentView: QWidget = self.mainWidget
        self.layout: QStackedLayout = QStackedLayout()
        self.layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.layout.addWidget(self.currentView)
        self.setLayout(self.layout)

    def clearCurrentView(self):
        if self.currentView:
            self.currentView = None

    def backMain(self):
        self.clearCurrentView()
        self.currentView = self.mainWidget
        self.layout.setCurrentWidget(self.currentView)

    def handleBtn1(self):
        self.clearCurrentView()
        self.buttons_class = Buttons()
        self.currentView = self.buttons_class
        self.currentView.backSignal.connect(self.backMain)
        self.layout.addWidget(self.currentView)
        self.layout.setCurrentWidget(self.currentView)

    def handleBtn2(self):
        self.clearCurrentView()
        self.line_edit_class = LineEdit()
        self.currentView = self.line_edit_class
        self.currentView.backSignal.connect(self.backMain)
        self.layout.addWidget(self.currentView)
        self.layout.setCurrentWidget(self.currentView)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec())