import sys
import os
import logging
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication

def create_directories():
    directories = ['logs', 'configs', 'output']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    create_directories()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("=== ЗАПУСК ПРИЛОЖЕНИЯ ===")
    
    try:
        app = QApplication(sys.argv)
        
        from ui.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        logger.info("Приложение запущено успешно")
        sys.exit(app.exec())
        
    except Exception as e:
        logger.critical(f"Ошибка: {e}")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        return 1

if __name__ == "__main__":
    main()
