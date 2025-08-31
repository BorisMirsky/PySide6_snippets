import os

from PySide6.QtGui import QFontDatabase, QFont


class StyleManager:
    @staticmethod
    def menu_button_style():
        return """
        QPushButton {
            padding: 10px; 
            border: 2px solid #8f8f91; 
            border-radius: 10px;
            font-size: 18pt;
            font-weight: bold; 
            background-color: #d4dbdb;
            text-transform: uppercase;
        }
        
                QPushButton:hover { 
            background-color: #A8DADC;  /* Цвет при наведении */
            border: 3px solid #1D3557; /* Рамка при наведении */
            font-weight: bold;
        }
        """
    @staticmethod
    def active_menu_button_style():
        return """ QPushButton {
                        padding: 10px; 
                        border: 3px solid #1D3557;
                        border-radius: 10px;
                        font-size: 18pt;
                        font-weight: bold; 
                        background-color: #A8DADC;
                        text-transform: uppercase;
                    }"""
    

    def window_title():
        return """
        
             background-color: white; 
            margin: 0; 
            padding: 5px 0 5px 5px; 
            max-height: 30px;

            border-bottom: 2px solid #eeeeee;
            
        """

    def window_title_version():
        return """
            color: #666666; 
            font-size: 12px;
            
        """


    @staticmethod
    def load_font():
        font_path = os.path.abspath("resources/fonts/MainFont.otf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        return QFont(font_families[0], 16) if font_families else QFont("Arial", 16)
