from pathlib import Path
import PySide6.QtWidgets as QtW
from PySide6.QtCore import QSize

from nav_parser.main_parser import Args, main


class MainWindow(QtW.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('NAV-parser')
        self.setFixedSize(QSize(600, 200))

        self.main_layout = QtW.QVBoxLayout()
        self.container = QtW.QWidget()
        self.container.setLayout(self.main_layout)

        self.setCentralWidget(self.container)

        # Добавление виджетов
        self.build_file_dialog()
        self.build_input()
        self.build_run_button()

    def build_file_dialog(self):
        file_layout = QtW.QHBoxLayout()
        label = QtW.QLabel('Выберите файл:')
        self.path = QtW.QLineEdit()
        file_browse = QtW.QPushButton('Обзор ...')
        file_browse.clicked.connect(self.open_file_dialog)

        file_layout.addWidget(label)
        file_layout.addWidget(self.path)
        file_layout.addWidget(file_browse)
        self.main_layout.addLayout(file_layout)

    def open_file_dialog(self):
        filename, ok = QtW.QFileDialog.getOpenFileName(self,
            filter="(*.nav)"
        )
        if filename:
            self.path.setText(str(Path(filename)))

    def build_input(self):
        layout = QtW.QGridLayout()

        label_start = QtW.QLabel('Начало:')
        self.start = self.spin_widget()
        layout.addWidget(label_start, 0, 0)
        layout.addWidget(self.start, 0, 1)

        stub = QtW.QLabel()
        stub.setFixedSize(200, 20)
        layout.addWidget(stub, 0, 2)

        label_finish = QtW.QLabel('Конец:')
        self.finish = self.spin_widget()
        layout.addWidget(label_finish, 0, 3)
        layout.addWidget(self.finish, 0, 4)
        self.main_layout.addLayout(layout)

    def spin_widget(self):
        spin = QtW.QSpinBox()
        spin.setRange(0, 1000000)
        return spin

    def build_run_button(self):
        button = QtW.QPushButton('Запуск')
        button.setFixedSize(200, 30)
        button.clicked.connect(self.run_parser)
        self.main_layout.addWidget(button)

    def show_message(self, text, message_type=None):
        match message_type:
            case 'info':    icon = QtW.QMessageBox.Icon.Information
            case 'warning': icon = QtW.QMessageBox.Icon.Warning
            case 'error':   icon = QtW.QMessageBox.Icon.Critical
            case None:      icon = QtW.QMessageBox.Icon.NoIcon

        msg = QtW.QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle("Сообщение")
        msg.setStandardButtons(QtW.QMessageBox.StandardButton.Ok)

        msg.exec()

    def run_parser(self):
        path = self.path.text()
        if not path:
            self.show_message('Выберите файл!', 'error')
            return
        print(
            f'Файл: {path}\n'
            f'Начало: {self.start.value()}\n'
            f'Конец: {self.finish.value()}\n'
        )
        args = Args(
            srcfile=path,
            start_step=self.start.value(),
            end_step=self.finish.value()
        )
        main(args)
        self.show_message('Завершено!', 'info')


app = QtW.QApplication([])
window = MainWindow()
window.show()
app.exec()
