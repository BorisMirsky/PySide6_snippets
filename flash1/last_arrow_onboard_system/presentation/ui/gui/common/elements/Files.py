# This Python file uses the following encoding: utf-8
from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
from PySide6.QtCore import QCoreApplication, Signal
from typing import Optional

class FileSelector(QWidget):
    filepathChanged: Signal = Signal(str)
    def __init__(self, filter: str = '*.*', init_path: Optional[str] = None, parent = None) ->None:
        super().__init__(parent)
        self.__filepathView = QLineEdit()
        self.__filepathView.setProperty('optionsWindowLineEdit', True)
        self.__filepathView.setReadOnly(True)
        self.__filepathView.setPlaceholderText(QCoreApplication.translate('Tools/select filepath', 'Selected file'))
        self.__filepathView.textChanged.connect(self.filepathChanged)
        self.__selectFileButton = QPushButton('...')
        self.__selectFileButton.setProperty("optionsWindowPushButton", True)
        self.__selectFileButton.clicked.connect(self.__selectFilepath)

        self.__filter = filter
        self.__filepathView.setText(init_path)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.__filepathView, 1)
        layout.addWidget(self.__selectFileButton, 0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

    def filepath(self) -> str:
        return self.__filepathView.text()

    def __selectFilepath(self) ->None:
        selectedFile = QFileDialog.getOpenFileName(self, QCoreApplication.translate('Tools/select filepath', 'Select program task'), '', self.__filter)[0]
        if len(selectedFile) != 0:
            self.__filepathView.setText(selectedFile)
