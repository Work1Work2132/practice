import sys
import os
import logging
from datetime import datetime
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QSlider, QLabel, QFileDialog, 
                            QGroupBox, QTextEdit, QMessageBox, QFrame,
                            QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QFont, QPalette, QColor

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from image_lib.image_processor import ImageProcessor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.processor = ImageProcessor()
        self.current_image = None
        self.original_image = None
        self.processed_image = None
        self.functional_buttons = []
        self.user_actions = []  # История действий пользователя
        self.setup_ui()
        self.apply_styles()
        
    def setup_ui(self):
        self.setWindowTitle("Image Processor")
        self.setGeometry(100, 100, 1200, 700)
        
        # Устанавливаем красивый фон
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Центральный виджет
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Левая панель - изображения
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)
        
        # Контейнер для двух изображений
        images_container = QHBoxLayout()
        
        # Исходное изображение
        original_frame = QFrame()
        original_frame.setFrameStyle(QFrame.Shape.Box)
        original_frame.setStyleSheet("QFrame { background-color: white; border: 2px solid #ccc; border-radius: 8px; }")
        original_layout = QVBoxLayout(original_frame)
        
        original_title = QLabel("Выбранное изображение")
        original_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        original_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        original_layout.addWidget(original_title)
        
        self.original_label = QLabel("Загрузить изображение")
        self.original_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.original_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa; 
                border: 2px dashed #aaa; 
                border-radius: 6px; 
                padding: 40px;
                color: #666;
                font-size: 14px;
                font-family: Segoe UI;
            }
        """)
        self.original_label.setMinimumSize(400, 300)
        original_layout.addWidget(self.original_label)
        images_container.addWidget(original_frame)
        
        # Обработанное изображение (предпросмотр)
        processed_frame = QFrame()
        processed_frame.setFrameStyle(QFrame.Shape.Box)
        processed_frame.setStyleSheet("QFrame { background-color: white; border: 2px solid #ccc; border-radius: 8px; }")
        processed_layout = QVBoxLayout(processed_frame)
        
        processed_title = QLabel("Предпросмотр")
        processed_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        processed_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        processed_layout.addWidget(processed_title)
        
        self.processed_label = QLabel("Обработанное изображение")
        self.processed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processed_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa; 
                border: 2px dashed #aaa; 
                border-radius: 6px; 
                padding: 40px;
                color: #666;
                font-size: 14px;
                font-family: Segoe UI;
            }
        """)
        self.processed_label.setMinimumSize(400, 300)
        processed_layout.addWidget(self.processed_label)
        images_container.addWidget(processed_frame)
        
        left_panel.addLayout(images_container)
        
        # Блок информации об изображении (техническая информация)
        image_info_frame = QFrame()
        image_info_frame.setFrameStyle(QFrame.Shape.Box)
        image_info_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #ddd; border-radius: 6px; }")
        image_info_layout = QVBoxLayout(image_info_frame)
        
        image_info_title = QLabel("Информация об изображении")
        image_info_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        image_info_layout.addWidget(image_info_title)
        
        self.image_info_text = QTextEdit()
        self.image_info_text.setMaximumHeight(80)
        self.image_info_text.setReadOnly(True)
        self.image_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: Segoe UI;
            }
        """)
        image_info_layout.addWidget(self.image_info_text)
        
        left_panel.addWidget(image_info_frame)
        
        # Блок информации о действиях пользователя (как в схеме задания)
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.Shape.Box)
        actions_frame.setStyleSheet("QFrame { background-color: white; border: 1px solid #ddd; border-radius: 6px; }")
        actions_layout = QVBoxLayout(actions_frame)
        
        actions_title = QLabel("Блок информации")
        actions_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        actions_layout.addWidget(actions_title)
        
        self.actions_text = QTextEdit()
        self.actions_text.setMaximumHeight(120)
        self.actions_text.setReadOnly(True)
        self.actions_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-size: 11px;
                font-family: Segoe UI;
            }
        """)
        self.actions_text.setPlaceholderText("Здесь будет отображаться история действий...")
        actions_layout.addWidget(self.actions_text)
        
        left_panel.addWidget(actions_frame)
        
        # Правая панель - управление
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        # Функциональные блоки
        functions_group = QGroupBox("Функциональные блоки")
        functions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold; 
                font-family: Segoe UI;
                font-size: 12px;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
            }
        """)
        functions_layout = QVBoxLayout(functions_group)
        
        # Кнопка загрузки
        self.btn_load = QPushButton("Загрузить изображение")
        self.btn_load.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                font-family: Segoe UI;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.btn_load.clicked.connect(self.load_image)
        functions_layout.addWidget(self.btn_load)
        
        # Блок камеры (заглушка)
        camera_label = QLabel("Блок камеры")
        camera_label.setFont(QFont("Segoe UI", 10))
        camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_label.setStyleSheet("background-color: #e9ecef; padding: 8px; border-radius: 4px; color: #666;")
        functions_layout.addWidget(camera_label)
        
        # Функциональные кнопки
        func_buttons_layout = QVBoxLayout()
        
        # Создаем функциональные кнопки с реальными функциями
        func_buttons = [
            ("Черно-белое", self.apply_grayscale),
            ("Сепия", self.apply_sepia),
            ("Инверсия", self.apply_invert),
            ("Размытие", self.apply_blur)
        ]
        
        for text, func in func_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-size: 11px;
                    font-family: Segoe UI;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QPushButton:disabled {
                    background-color: #ccc;
                    color: #666;
                }
            """)
            btn.clicked.connect(func)
            btn.setEnabled(False)
            func_buttons_layout.addWidget(btn)
            self.functional_buttons.append(btn)
        
        functions_layout.addLayout(func_buttons_layout)
        right_panel.addWidget(functions_group)
        
        # Настройки обработки
        settings_group = QGroupBox("Настройки обработки")
        settings_group.setStyleSheet(functions_group.styleSheet())
        settings_layout = QVBoxLayout(settings_group)
        
        # Яркость
        brightness_layout = QVBoxLayout()
        brightness_label = QLabel("Яркость")
        brightness_label.setFont(QFont("Segoe UI", 10))
        brightness_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(0, 200)
        self.brightness_slider.setValue(100)
        self.brightness_slider.valueChanged.connect(self.apply_adjustments)
        self.brightness_slider.setEnabled(False)
        brightness_layout.addWidget(self.brightness_slider)
        
        brightness_value_layout = QHBoxLayout()
        self.brightness_value = QLabel("1.00")
        self.brightness_value.setFont(QFont("Segoe UI", 9))
        self.brightness_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brightness_value_layout.addWidget(QLabel("Темнее"))
        brightness_value_layout.addWidget(self.brightness_value)
        brightness_value_layout.addWidget(QLabel("Ярче"))
        brightness_layout.addLayout(brightness_value_layout)
        
        settings_layout.addLayout(brightness_layout)
        
        # Контраст
        settings_layout.addSpacing(10)
        
        contrast_layout = QVBoxLayout()
        contrast_label = QLabel("Контраст")
        contrast_label.setFont(QFont("Segoe UI", 10))
        contrast_layout.addWidget(contrast_label)
        
        self.contrast_slider = QSlider(Qt.Orientation.Horizontal)
        self.contrast_slider.setRange(0, 200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.apply_adjustments)
        self.contrast_slider.setEnabled(False)
        contrast_layout.addWidget(self.contrast_slider)
        
        contrast_value_layout = QHBoxLayout()
        self.contrast_value = QLabel("1.00")
        self.contrast_value.setFont(QFont("Segoe UI", 9))
        self.contrast_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        contrast_value_layout.addWidget(QLabel("Меньше"))
        contrast_value_layout.addWidget(self.contrast_value)
        contrast_value_layout.addWidget(QLabel("Больше"))
        contrast_layout.addLayout(contrast_value_layout)
        
        settings_layout.addLayout(contrast_layout)
        
        # Изменение размера
        settings_layout.addSpacing(10)
        
        resize_layout = QVBoxLayout()
        resize_label = QLabel("Изменение размера")
        resize_label.setFont(QFont("Segoe UI", 10))
        resize_layout.addWidget(resize_label)
        
        resize_controls_layout = QHBoxLayout()
        
        # Ширина
        width_layout = QVBoxLayout()
        width_label = QLabel("Ширина:")
        width_label.setFont(QFont("Segoe UI", 9))
        width_layout.addWidget(width_label)
        
        self.width_spinbox = QSpinBox()
        self.width_spinbox.setRange(1, 5000)
        self.width_spinbox.setValue(800)
        self.width_spinbox.setEnabled(False)
        self.width_spinbox.setStyleSheet("""
            QSpinBox {
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-family: Segoe UI;
            }
        """)
        width_layout.addWidget(self.width_spinbox)
        resize_controls_layout.addLayout(width_layout)
        
        # Высота
        height_layout = QVBoxLayout()
        height_label = QLabel("Высота:")
        height_label.setFont(QFont("Segoe UI", 9))
        height_layout.addWidget(height_label)
        
        self.height_spinbox = QSpinBox()
        self.height_spinbox.setRange(1, 5000)
        self.height_spinbox.setValue(600)
        self.height_spinbox.setEnabled(False)
        self.height_spinbox.setStyleSheet(self.width_spinbox.styleSheet())
        height_layout.addWidget(self.height_spinbox)
        resize_controls_layout.addLayout(height_layout)
        
        resize_layout.addLayout(resize_controls_layout)
        
        # Кнопка применения размера
        self.btn_resize = QPushButton("Применить размер")
        self.btn_resize.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 6px 10px;
                border-radius: 3px;
                font-size: 10px;
                font-family: Segoe UI;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.btn_resize.clicked.connect(self.apply_resize)
        self.btn_resize.setEnabled(False)
        resize_layout.addWidget(self.btn_resize)
        
        settings_layout.addLayout(resize_layout)
        right_panel.addWidget(settings_group)
        
        # Кнопки управления
        control_group = QGroupBox("Управление")
        control_group.setStyleSheet(functions_group.styleSheet())
        control_layout = QVBoxLayout(control_group)
        
        self.btn_save = QPushButton("Сохранить результат")
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                font-family: Segoe UI;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #EF6C00;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.btn_save.clicked.connect(self.save_image)
        self.btn_save.setEnabled(False)
        control_layout.addWidget(self.btn_save)
        
        self.btn_undo = QPushButton("Отменить (Undo)")
        self.btn_undo.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-size: 11px;
                font-family: Segoe UI;
            }
            QPushButton:hover {
                background-color: #757575;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.btn_undo.clicked.connect(self.undo_action)
        self.btn_undo.setEnabled(False)
        control_layout.addWidget(self.btn_undo)
        
        right_panel.addWidget(control_group)
        
        # Добавляем растягивающийся спейсер внизу
        right_panel.addStretch()
        
        # Добавляем панели
        main_layout.addLayout(left_panel, 70)
        main_layout.addLayout(right_panel, 30)
    
    def apply_styles(self):
        slider_style = """
            QSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #e0e0e0;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 1px solid #1976D2;
                width: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
            }
        """
        self.brightness_slider.setStyleSheet(slider_style)
        self.contrast_slider.setStyleSheet(slider_style)
    
    def log_action(self, action, details=""):
        """Добавляет действие в историю и обновляет блок информации"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        action_text = f"[{timestamp}] {action}"
        if details:
            action_text += f" - {details}"
        
        self.user_actions.append(action_text)
        
        # Ограничиваем историю последними 10 действиями
        if len(self.user_actions) > 10:
            self.user_actions = self.user_actions[-10:]
        
        # Обновляем отображение
        self.actions_text.setText("\n".join(self.user_actions))
        
        # Прокручиваем вниз
        cursor = self.actions_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.actions_text.setTextCursor(cursor)
    
    def enable_controls(self, enabled):
        """Включает/выключает все элементы управления"""
        controls = [
            self.brightness_slider, self.contrast_slider,
            self.btn_save, self.btn_undo, self.btn_resize,
            self.width_spinbox, self.height_spinbox
        ] + self.functional_buttons
        
        for control in controls:
            if control:
                control.setEnabled(enabled)
    
    def load_image(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Выберите изображение", "", 
                "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.gif);;All Files (*)"
            )
            if file_path:
                self.current_image = self.processor.load_image(file_path)
                self.original_image = self.current_image.copy()
                self.processed_image = self.current_image.copy()
                
                # Отображаем оба изображения
                self.display_image(self.current_image, self.original_label)
                self.display_image(self.processed_image, self.processed_label)
                
                # Обновляем техническую информацию
                info = self.processor.get_image_info(self.current_image)
                info_text = f"Ширина: {info['width']} px\n"
                info_text += f"Высота: {info['height']} px\n"
                info_text += f"Формат: {info['format']}\n"
                info_text += f"Режим: {info['mode']}"
                self.image_info_text.setText(info_text)
                
                # Логируем действие
                filename = os.path.basename(file_path)
                self.log_action("Загружено изображение", f"'{filename}' ({info['width']}x{info['height']})")
                
                # Устанавливаем текущие размеры в спинбоксы
                self.width_spinbox.setValue(self.current_image.width)
                self.height_spinbox.setValue(self.current_image.height)
                
                # Активируем элементы управления
                self.brightness_slider.setValue(100)
                self.contrast_slider.setValue(100)
                self.enable_controls(True)
                
                logging.info(f"Изображение загружено: {file_path}")
                
        except Exception as e:
            logging.error(f"Ошибка загрузки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение:\n{str(e)}")
    
    def apply_adjustments(self):
        if self.current_image is None:
            return
        
        try:
            brightness = self.brightness_slider.value() / 100.0
            contrast = self.contrast_slider.value() / 100.0
            
            self.brightness_value.setText(f"{brightness:.2f}")
            self.contrast_value.setText(f"{contrast:.2f}")
            
            # Применяем корректировки к копии изображения для предпросмотра
            self.processed_image = self.processor.adjust_brightness(self.current_image, brightness)
            self.processed_image = self.processor.adjust_contrast(self.processed_image, contrast)
            
            # Отображаем результат в предпросмотре
            self.display_image(self.processed_image, self.processed_label)
            
            # Логируем изменение параметров
            if brightness != 1.0 or contrast != 1.0:
                params = []
                if brightness != 1.0:
                    params.append(f"яркость: {brightness:.2f}")
                if contrast != 1.0:
                    params.append(f"контраст: {contrast:.2f}")
                self.log_action("Корректировка", ", ".join(params))
            
        except Exception as e:
            logging.error(f"Ошибка обработки: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка обработки:\n{str(e)}")
    
    def apply_resize(self):
        if self.current_image is None:
            return
        
        try:
            width = self.width_spinbox.value()
            height = self.height_spinbox.value()
            
            # Применяем изменение размера к обработанному изображению
            self.processed_image = self.processor.resize_image(self.current_image, width, height)
            self.display_image(self.processed_image, self.processed_label)
            
            # Обновляем техническую информацию
            info = self.processor.get_image_info(self.processed_image)
            info_text = f"Ширина: {info['width']} px\n"
            info_text += f"Высота: {info['height']} px\n"
            info_text += f"Формат: {info['format']}\n"
            info_text += f"Режим: {info['mode']}"
            self.image_info_text.setText(info_text)
            
            # Логируем действие
            self.log_action("Изменен размер", f"{width}x{height} px")
            
            logging.info(f"Изменен размер: {width}x{height}")
            
        except Exception as e:
            logging.error(f"Ошибка изменения размера: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка изменения размера:\n{str(e)}")
    
    # ===== ФУНКЦИОНАЛЬНЫЕ КНОПКИ =====
    def apply_grayscale(self):
        try:
            self.processed_image = self.processor.apply_grayscale(self.current_image)
            self.display_image(self.processed_image, self.processed_label)
            self.log_action("Применен фильтр", "Черно-белое")
        except Exception as e:
            self.show_error("Ошибка Ч/Б фильтра", str(e))
    
    def apply_sepia(self):
        try:
            self.processed_image = self.processor.apply_sepia(self.current_image)
            self.display_image(self.processed_image, self.processed_label)
            self.log_action("Применен фильтр", "Сепия")
        except Exception as e:
            self.show_error("Ошибка сепии", str(e))
    
    def apply_invert(self):
        try:
            self.processed_image = self.processor.apply_invert(self.current_image)
            self.display_image(self.processed_image, self.processed_label)
            self.log_action("Применен фильтр", "Инверсия")
        except Exception as e:
            self.show_error("Ошибка инвертирования", str(e))
    
    def apply_blur(self):
        try:
            self.processed_image = self.processor.apply_blur(self.current_image)
            self.display_image(self.processed_image, self.processed_label)
            self.log_action("Применен фильтр", "Размытие")
        except Exception as e:
            self.show_error("Ошибка размытия", str(e))
    
    def display_image(self, image, label):
        try:
            if image.mode == "RGB":
                qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format.Format_RGB888)
            elif image.mode == "RGBA":
                qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format.Format_RGBA8888)
            else:
                image = image.convert("RGB")
                qimage = QImage(image.tobytes(), image.width, image.height, QImage.Format.Format_RGB888)
            
            pixmap = QPixmap.fromImage(qimage)
            scaled = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            label.setPixmap(scaled)
            
        except Exception as e:
            logging.error(f"Ошибка отображения: {e}")
    
    def save_image(self):
        if self.processed_image is None:
            QMessageBox.warning(self, "Предупреждение", "Нет изображения для сохранения")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить изображение", "обработанное_изображение", 
                "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;All Files (*)"
            )
            
            if file_path:
                self.processor.save_image(self.processed_image, file_path)
                QMessageBox.information(self, "Успех", "Изображение успешно сохранено!")
                self.log_action("Сохранение", os.path.basename(file_path))
                logging.info(f"Изображение сохранено: {file_path}")
                
        except Exception as e:
            logging.error(f"Ошибка сохранения: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения:\n{str(e)}")
    
    def undo_action(self):
        if self.original_image:
            # Восстанавливаем оригинальное изображение
            self.current_image = self.original_image.copy()
            self.processed_image = self.original_image.copy()
            
            # Отображаем оба изображения
            self.display_image(self.current_image, self.original_label)
            self.display_image(self.processed_image, self.processed_label)
            
            # Сбрасываем слайдеры
            self.brightness_slider.setValue(100)
            self.contrast_slider.setValue(100)
            self.brightness_value.setText("1.00")
            self.contrast_value.setText("1.00")
            
            # Восстанавливаем оригинальные размеры
            self.width_spinbox.setValue(self.original_image.width)
            self.height_spinbox.setValue(self.original_image.height)
            
            # Логируем действие
            self.log_action("Отмена", "Все изменения отменены")
            
            logging.info("Действие отменено")
    
    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
