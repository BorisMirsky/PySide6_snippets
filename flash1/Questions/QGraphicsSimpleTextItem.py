from PySide6 import QtGui
from PySide6.QtWidgets import QApplication, QMainWindow, QGraphicsScene,QGraphicsView, QGraphicsItem, QGraphicsPixmapItem, QGraphicsSimpleTextItem
from PySide6.QtGui import QPixmap, QPainter
#from PySide6.Qt import Qt

import sys


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = "Изображение в PyQt5"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 400

        self.setWindowTitle(self.title)
        # Задание местоположения и размера окна
        self.setGeometry(self.left, self.top, self.width, self.height)
        # Создание графической сцены
        self.scene = QGraphicsScene()
        # Создание инструмента для отрисовки графической сцены
        self.graphicView = QGraphicsView(self.scene, self)
        # Задание местоположения и размера графической сцены
        self.graphicView.setGeometry(0, 0, self.width, self.height)

    def plot(self):
        # Создание объекта QPixmap
        picture = QPixmap('IMG2.jpg')
        # Создание "пустого" объекта QGraphicsPixmapItem
        image = QGraphicsPixmapItem()
        # Задание изображения в объект QGraphicsPixmapItem
        image.setPixmap(picture)
        # Позиция объекта QGraphicsPixmapItem
        image.setOffset(0, 0)
        # Добавление объекта QGraphicsPixmapItem на сцену
        self.scene.addItem(image)

        # Создание объекта QGraphicsSimpleTextItem
        text = QGraphicsSimpleTextItem('Пример текста')
        # Задание позиции текста
        text.setX(0)
        text.setY(200)
        # Добавление текста на сцену
        self.scene.addItem(text)


App = QApplication(sys.argv)
window = Window()
window.show()  # Демонстрация окна
window.plot()  # Построение и перерисовка окна

sys.exit(App.exec())