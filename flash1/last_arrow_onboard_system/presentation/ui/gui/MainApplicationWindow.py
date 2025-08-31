# This Python file uses the following encoding: utf-8
import time

from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout, QPushButton, QVBoxLayout, QLabel, QFileDialog, QGridLayout
from PySide6.QtCore import QTimer, QCoreApplication, Signal, Qt
import pandas
import gc
import cProfile

from operating.states.ApplicationStateMachine import ApplicationStateMachine
from operating.states.program_task_calculation.ProgramTaskCalculationState import ProgramTaskCalculationSuccessState
from resources.style.StyleManager import StyleManager
from .idle.IdleView import IdleView
from .program_task_calculation.ProgramTaskCalculationView import ProgramTaskCalculationView
from .maintenance.MaintenanceView import MaintenanceView
from .measuring.MeasuringView import MeasuringView
from .lining.LiningView import LiningView, SelectLiningTripModeView
from presentation.ui.gui.common.elements.Base import setWindowTitle

class ApplicationView(QWidget):
    def __init__(self, state: ApplicationStateMachine, parent: QWidget = None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_KeyCompression, True)  #  Фикс для Mac клавиатуры
        # self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  #  Фикс для Mac клавиатуры

        # disable [x]
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMinMaxButtonsHint)
        #
        #self.showFullScreen()     # -> all views inherit fullSizeScreen
        #
        self.__state: ApplicationStateMachine = state
        #self.__state1: ProgramTaskCalculationSuccessState = state1
        self.__state.idle.entered.connect(self.__onIdleStateEntered)
        self.__state.idle.exited.connect(self.__onIdleStateExited)
        self.__state.programTaskCalculation.entered.connect(self.__onProgramTaskCalculationStateEntered)
        self.__state.programTaskCalculation.exited.connect(self.__onProgramTaskCalculationStateExited)
        self.__state.maintenance.entered.connect(self.__onMaintenanceStateEntered)
        self.__state.maintenance.exited.connect(self.__onMaintenanceStateExited)
        self.__state.measuring.entered.connect(self.__onMeasuringStateEntered)
        self.__state.measuring.exited.connect(self.__onMeasuringStateExited)
        self.__state.lining.entered.connect(self.__onLiningStateEntered)
        self.__state.lining.exited.connect(self.__onLiningStateExited)
        self.__state.quit.entered.connect(self.__onQuitStateEntered)
        self.__state.quit.exited.connect(self.__onQuitStateExited)

        self.__currentView: QWidget = None
        self.__layout: QStackedLayout = QStackedLayout()
        self.__layout.setStackingMode(QStackedLayout.StackingMode.StackOne)
        self.setLayout(self.__layout)

        # screen_geometry = QApplication.primaryScreen().availableGeometry()
        # screen_geometry.setHeight(screen_geometry.height() - 30)
        # self.setGeometry(screen_geometry) 
        # self.setMinimumSize(screen_geometry.width(), screen_geometry.height()) 
        # self.resize(screen_geometry.size())
        
        self.showFullScreen()

        self.setWindowTitle("ПАК «Стрела-ДС»")

    def __onIdleStateEntered(self) ->None:
        gc.collect()
        self.__currentView = IdleView(self.__state.idle)
        self.__layout.addWidget(self.__currentView)
        self.setWindowTitle("ПАК «Стрела-ДС»")

    def __onIdleStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onProgramTaskCalculationStateEntered(self) ->None:
        gc.collect()
        self.__currentView = ProgramTaskCalculationView(self.__state.programTaskCalculation)
        self.__layout.addWidget(self.__currentView)
    def __onProgramTaskCalculationStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onMaintenanceStateEntered(self) ->None:
        gc.collect()
        self.__currentView = MaintenanceView(self.__state.maintenance)
        self.__layout.addWidget(self.__currentView)
    def __onMaintenanceStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onMeasuringStateEntered(self) ->None:
        gc.collect()
        self.__currentView = MeasuringView(self.__state.measuring)
        self.__layout.addWidget(self.__currentView)
    def __onMeasuringStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onLiningStateEntered(self) ->None:
        gc.collect()
        self.__currentView = LiningView(self.__state.lining)  #, self.__state1)
        self.__layout.addWidget(self.__currentView)
    def __onLiningStateExited(self) ->None:
        gc.collect()
        self.__currentView.deleteLater()
    def __onQuitStateEntered(self) ->None:
        gc.collect()
        pass
    def __onQuitStateExited(self) ->None:
        gc.collect()
        pass

    # def set_initial_focus(self):
    #     """Ставим фокус на первую кнопку"""
    #     if self.__currentView:
    #         buttons = self.__currentView.findChildren(QPushButton)
    #         if buttons:
    #             buttons[0].setFocus()
    #             self.update_button_focus()
    # def set_initial_focus(self):
    #     """Ставим фокус на первую кнопку"""
    #     if self.__currentView:
    #         buttons = self.__currentView.findChildren(QPushButton)
    #         if buttons:
    #             buttons[0].setFocus()

    # def keyPressEvent(self, event):
    #     """Обрабатывает `Tab`, `Shift+Tab` и `Enter` """
    #
    #     """Обработка кнопки ESCAPE в окне выправки!"""
    #     if event.key() == Qt.Key.Key_Escape and self.__currentView.findChild(SelectLiningTripModeView):
    #         self.__currentView.findChild(SelectLiningTripModeView).handle_escape()  # ✅ Вместо `keyPressEvent()`, вызываем `handle_escape()`
    #         event.accept()
    #         return
    #
    #     active_view = None
    #     # Проверяем, находится ли пользователь в `IdleView`
    #     if isinstance(self.__currentView, IdleView):
    #         active_view = self.__currentView
    #     # Проверяем, находится ли `SelectLiningTripModeView` внутри `LiningView`
    #     elif self.__currentView:
    #         active_view = self.__currentView.findChild(SelectLiningTripModeView)
    #     # Если активного окна нет, выходим
    #     if not isinstance(active_view, (IdleView, SelectLiningTripModeView)):
    #         return
    #
    #     if self.__currentView:
    #         buttons = self.__currentView.findChildren(QPushButton)
    #
    #         if not buttons:
    #             return  # Если кнопок нет, ничего не делаем
    #
    #         focused_button = QApplication.focusWidget()
    #
    #         if isinstance(focused_button, QPushButton) and focused_button in buttons:
    #             current_index = buttons.index(focused_button)
    #         else:
    #             current_index = -1  # Если фокуса нет, устанавливаем первую кнопку при первом нажатии
    #
    #         new_index = current_index  # Начинаем с текущего индекса
    #
    #         if event.key() == Qt.Key.Key_Tab:
    #             new_index = (current_index + 1) % len(buttons)
    #
    #         elif event.key() == Qt.Key.Key_Backtab:  # Shift+Tab (переключение назад)
    #             new_index = (current_index - 1) % len(buttons)
    #
    #         elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
    #             if current_index != -1:
    #                 buttons[current_index].click()
    #             return
    #
    #         # Если индекс изменился, обновляем фокус
    #         if new_index != current_index:
    #             buttons[new_index].setFocus()
    #             QApplication.processEvents()
    #             self.update_button_focus(buttons[new_index])
    #
    #         event.accept()

    # def update_button_focus(self, active_button):
    #     """Обновляет стиль только для активной кнопки"""
    #     if not self.__currentView or not isinstance(active_button, QPushButton):
    #         return
    #
    #     # Сбрасываем стиль всех кнопок
    #     buttons = self.__currentView.findChildren(QPushButton)
    #     for button in buttons:
    #         button.setStyleSheet(StyleManager.menu_button_style())
    #
    #     # Выделяем активную кнопку
    #     active_button.setStyleSheet(
    #         "QPushButton { background-color: #A8DADC; border: 3px solid #1D3557; font-weight: bold; }"
    #     )
    #
    #     self.repaint()  # Принудительная перерисовка окна
