from PySide6.QtWidgets import * #QVBoxLayout, QApplication
#from PySide6.QtCharts import * #QLineSeries, QChart, QChartView, QValueAxis
from PySide6.QtCore import * #QColor, QBrush
import sys
#import math
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 


class MouseEventApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mouse Event Example")
        self.setGeometry(100, 100, 400, 200)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.mouse_label = QLabel("Mouse Events:", self.central_widget)
        self.mouse_label.setGeometry(10, 10, 200, 30)

        self.mouse_tracker_label = QLabel("", self.central_widget)
        self.mouse_tracker_label.setGeometry(10, 40, 300, 30)

        # Install an event filter to capture mouse events
        self.central_widget.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseMove:
            x = event.x()
            y = event.y()
            self.mouse_tracker_label.setText(f"Mouse moved to ({x}, {y})")

        elif event.type() == QEvent.MouseButtonPress:
            button = ""
            if event.button() == Qt.LeftButton:
                button = "Left"
            elif event.button() == Qt.RightButton:
                button = "Right"
            elif event.button() == Qt.MiddleButton:
                button = "Middle"

            self.mouse_tracker_label.setText(f"{button} button clicked")

        return super().eventFilter(obj, event)

def main():
    app = QApplication(sys.argv)
    window = MouseEventApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
