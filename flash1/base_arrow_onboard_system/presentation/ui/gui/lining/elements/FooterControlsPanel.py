from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget, QLabel
from PySide6.QtCore import Qt, Signal

class FooterControlsPanel(QWidget):
    pathAdjustmentActivated: Signal = Signal()
    emergencyExtraction: Signal = Signal()
    quitButtonClicked: Signal = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        selector_button = QPushButton('Задатчик')
        mode_selector_button = QPushButton('Режим')
        review_button = QPushButton('Обзор [F3]')
        path_adjustement_button = QPushButton('Корректировка пути [F4]')               
        path_adjustement_button.clicked.connect(self.pathAdjustmentActivated)
        marker_button = QPushButton('Маркер [F5]')
        mechanism_retraction_button = QPushButton('Отвод [F8]')
        mechanism_retraction_button.clicked.connect(self.emergencyExtraction)
        quit_button = QPushButton('Выход [ESC]')

        selector_button.setEnabled(False)
        mode_selector_button.setEnabled(False)
        review_button.setEnabled(False)
        marker_button.setEnabled(False)
        quit_button.clicked.connect(self.quitButtonClicked)

        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(selector_button, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('Общая подъёмка'), Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(mode_selector_button, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel('Ручной'), Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(1)
        layout.addWidget(review_button, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(path_adjustement_button, Qt.AlignmentFlag.AlignRight) 
        layout.addWidget(marker_button, Qt.AlignmentFlag.AlignLeft)
        layout.addStretch(3)
        layout.addWidget(mechanism_retraction_button, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(quit_button, Qt.AlignmentFlag.AlignLeft)


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    w = FooterControlsPanel()
    w.show()
    sys.exit(app.exec())
