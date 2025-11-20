import logging
import json
import os
from datetime import datetime
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import numpy as np

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.history_file = "user_history.json"
        self._init_history()
    
    def _init_history(self):
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump([], f)
    
    def _log_operation(self, operation: str, parameters: dict):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            history.append({
                "date": datetime.now().isoformat(),
                "operation": operation,
                "parameters": parameters
            })
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Ошибка при записи истории: {e}")
    
    def validate_image(self, image_path: str) -> bool:
        if not os.path.exists(image_path):
            logger.error(f"Файл не существует: {image_path}")
            return False
        
        supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif')
        if not image_path.lower().endswith(supported_formats):
            logger.error(f"Неподдерживаемый формат файла: {image_path}")
            return False
        
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True
        except Exception as e:
            logger.error(f"Ошибка при проверке изображения: {e}")
            return False
    
    def load_image(self, image_path: str) -> Image.Image:
        if not self.validate_image(image_path):
            raise ValueError("Некорректный файл изображения")
        
        self._log_operation("load_image", {"file_path": image_path})
        logger.info(f"Загружено изображение: {image_path}")
        return Image.open(image_path)
    
    def get_image_info(self, image: Image.Image) -> dict:
        info = {
            "width": image.width,
            "height": image.height,
            "format": image.format,
            "mode": image.mode
        }
        
        logger.info(f"Получена информация об изображении: {info}")
        return info
    
    def save_image(self, image: Image.Image, file_path: str, format: str = None) -> None:
        if format is None:
            format = os.path.splitext(file_path)[1][1:].upper()
        
        image.save(file_path, format=format)
        
        self._log_operation("save_image", {"file_path": file_path, "format": format})
        logger.info(f"Изображение сохранено: {file_path} в формате {format}")
    
    # ===== ОСНОВНЫЕ КОРРЕКЦИИ =====
    def adjust_brightness(self, image: Image.Image, factor: float) -> Image.Image:
        if factor < 0:
            raise ValueError("Коэффициент яркости не может быть отрицательным")
        
        enhancer = ImageEnhance.Brightness(image)
        result = enhancer.enhance(factor)
        
        self._log_operation("adjust_brightness", {"brightness_factor": factor})
        logger.info(f"Изменена яркость: коэффициент {factor}")
        return result
    
    def adjust_contrast(self, image: Image.Image, factor: float) -> Image.Image:
        if factor < 0:
            raise ValueError("Коэффициент контраста не может быть отрицательным")
        
        enhancer = ImageEnhance.Contrast(image)
        result = enhancer.enhance(factor)
        
        self._log_operation("adjust_contrast", {"contrast_factor": factor})
        logger.info(f"Изменен контраст: коэффициент {factor}")
        return result
    
    def adjust_saturation(self, image: Image.Image, factor: float) -> Image.Image:
        if factor < 0:
            raise ValueError("Коэффициент насыщенности не может быть отрицательным")
        
        enhancer = ImageEnhance.Color(image)
        result = enhancer.enhance(factor)
        
        self._log_operation("adjust_saturation", {"saturation_factor": factor})
        logger.info(f"Изменена насыщенность: коэффициент {factor}")
        return result
    
    # ===== ОСНОВНЫЕ ФИЛЬТРЫ =====
    def apply_grayscale(self, image: Image.Image) -> Image.Image:
        result = image.convert('L').convert('RGB')
        self._log_operation("apply_grayscale", {})
        logger.info("Применен Ч/Б фильтр")
        return result
    
    def apply_invert(self, image: Image.Image) -> Image.Image:
        result = ImageOps.invert(image.convert('RGB'))
        self._log_operation("apply_invert", {})
        logger.info("Применена инверсия цветов")
        return result
    
    def apply_sepia(self, image: Image.Image) -> Image.Image:
        # Простая реализация сепии
        result = image.convert('RGB')
        width, height = result.size
        pixels = result.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = result.getpixel((px, py))
                
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[px, py] = (
                    min(255, tr),
                    min(255, tg),
                    min(255, tb)
                )
        
        self._log_operation("apply_sepia", {})
        logger.info("Применен сепия фильтр")
        return result
    
    # ===== ЦВЕТОВЫЕ ПРЕСЕТЫ =====
    def apply_warm_tone(self, image: Image.Image) -> Image.Image:
        # Теплые тона - увеличиваем красный и желтый
        result = image.convert('RGB')
        enhancer = ImageEnhance.Color(result)
        result = enhancer.enhance(1.2)
        
        # Добавляем теплый оттенок
        width, height = result.size
        pixels = result.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = result.getpixel((px, py))
                pixels[px, py] = (
                    min(255, int(r * 1.1)),
                    min(255, int(g * 1.05)),
                    b
                )
        
        self._log_operation("apply_warm_tone", {})
        logger.info("Применены теплые тона")
        return result
    
    def apply_cool_tone(self, image: Image.Image) -> Image.Image:
        # Холодные тона - увеличиваем синий и голубой
        result = image.convert('RGB')
        
        width, height = result.size
        pixels = result.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = result.getpixel((px, py))
                pixels[px, py] = (
                    r,
                    min(255, int(g * 1.05)),
                    min(255, int(b * 1.1))
                )
        
        self._log_operation("apply_cool_tone", {})
        logger.info("Применены холодные тона")
        return result
    
    def apply_vintage(self, image: Image.Image) -> Image.Image:
        # Винтажный эффект - сепия + снижение насыщенности
        result = self.apply_sepia(image)
        enhancer = ImageEnhance.Color(result)
        result = enhancer.enhance(0.8)
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(0.9)
        
        self._log_operation("apply_vintage", {})
        logger.info("Применен винтажный эффект")
        return result
    
    # ===== СПЕЦИАЛЬНЫЕ ЭФФЕКТЫ =====
    def auto_contrast(self, image: Image.Image) -> Image.Image:
        result = ImageOps.autocontrast(image.convert('RGB'))
        self._log_operation("auto_contrast", {})
        logger.info("Применен автоконтраст")
        return result
    
    def white_balance(self, image: Image.Image) -> Image.Image:
        # Простой баланс белого - выравнивание цветовых каналов
        result = image.convert('RGB')
        r, g, b = result.split()
        
        # Находим средние значения каналов
        r_avg = np.mean(np.array(r))
        g_avg = np.mean(np.array(g))
        b_avg = np.mean(np.array(b))
        
        # Выравниваем каналы
        avg = (r_avg + g_avg + b_avg) / 3
        r = r.point(lambda x: x * (avg / r_avg))
        g = g.point(lambda x: x * (avg / g_avg))
        b = b.point(lambda x: x * (avg / b_avg))
        
        result = Image.merge('RGB', (r, g, b))
        
        self._log_operation("white_balance", {})
        logger.info("Применен баланс белого")
        return result
    
    def black_point(self, image: Image.Image) -> Image.Image:
        # Коррекция черной точки - увеличиваем контраст в тенях
        result = image.convert('RGB')
        result = ImageOps.autocontrast(result, cutoff=2)
        
        self._log_operation("black_point", {})
        logger.info("Применена коррекция черной точки")
        return result
    
    def blue_tone(self, image: Image.Image) -> Image.Image:
        # Усиление синих тонов
        result = image.convert('RGB')
        width, height = result.size
        pixels = result.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = result.getpixel((px, py))
                pixels[px, py] = (
                    int(r * 0.9),
                    int(g * 0.95),
                    min(255, int(b * 1.2))
                )
        
        self._log_operation("blue_tone", {})
        logger.info("Применен синий тон")
        return result
    
    def skin_tone_enhance(self, image: Image.Image) -> Image.Image:
        # Улучшение тона кожи - теплые оттенки
        result = image.convert('RGB')
        width, height = result.size
        pixels = result.load()
        
        for py in range(height):
            for px in range(width):
                r, g, b = result.getpixel((px, py))
                # Увеличиваем красный и уменьшаем синий для теплого тона кожи
                pixels[px, py] = (
                    min(255, int(r * 1.1)),
                    min(255, int(g * 1.05)),
                    int(b * 0.9)
                )
        
        self._log_operation("skin_tone_enhance", {})
        logger.info("Применено улучшение тона кожи")
        return result
    
    def vibrance(self, image: Image.Image) -> Image.Image:
        # Вибрация - усиление насыщенности менее насыщенных цветов
        result = image.convert('RGB')
        enhancer = ImageEnhance.Color(result)
        result = enhancer.enhance(1.3)
        
        self._log_operation("vibrance", {})
        logger.info("Применена вибрация")
        return result
    
    # ===== ХУДОЖЕСТВЕННЫЕ ЭФФЕКТЫ =====
    def apply_blur(self, image: Image.Image) -> Image.Image:
        result = image.filter(ImageFilter.BLUR)
        self._log_operation("apply_blur", {})
        logger.info("Применено размытие")
        return result
    
    def apply_sharpen(self, image: Image.Image) -> Image.Image:
        result = image.filter(ImageFilter.SHARPEN)
        self._log_operation("apply_sharpen", {})
        logger.info("Применена резкость")
        return result
    
    def apply_emboss(self, image: Image.Image) -> Image.Image:
        result = image.filter(ImageFilter.EMBOSS)
        self._log_operation("apply_emboss", {})
        logger.info("Применено тиснение")
        return result
    
    def resize_image(self, image: Image.Image, width: int, height: int) -> Image.Image:
        if width <= 0 or height <= 0:
            raise ValueError("Ширина и высота должны быть положительными числами")
        
        result = image.resize((width, height), Image.Resampling.LANCZOS)
        
        self._log_operation("resize_image", {"new_width": width, "new_height": height})
        logger.info(f"Изменен размер: {width}x{height}")
        return result
      
