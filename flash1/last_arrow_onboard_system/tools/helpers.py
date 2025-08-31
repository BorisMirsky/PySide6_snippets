from PySide6.QtWidgets import QPushButton, QSizePolicy
from PySide6.QtCore import QCoreApplication

class ButtonFactory:
    @staticmethod
    def create_button(text, callback, font):
        """Создает кнопку с заданным текстом, стилем и обработчиком нажатия"""
        button = QPushButton(QCoreApplication.translate('App', text))
        button.clicked.connect(callback)
        button.setFont(font)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return button
