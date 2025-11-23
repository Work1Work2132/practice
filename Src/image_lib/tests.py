import unittest
import os
from PIL import Image
from image_processor import ImageProcessor

class TestImageProcessor(unittest.TestCase):
    """Модульные тесты для ImageProcessor"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.processor = ImageProcessor()
        self.test_image = Image.new('RGB', (100, 100), color='red')
        self.test_path = "test_image.png"
        self.test_image.save(self.test_path)
    
    def tearDown(self):
        """Очистка после тестов"""
        if os.path.exists(self.test_path):
            os.remove(self.test_path)
    
    def test_validate_image_valid(self):
        """Тест валидации корректного изображения"""
        self.assertTrue(self.processor.validate_image(self.test_path))
    
    def test_validate_image_invalid_path(self):
        """Тест валидации несуществующего файла"""
        self.assertFalse(self.processor.validate_image("nonexistent.jpg"))
    
    def test_adjust_brightness(self):
        """Тест изменения яркости"""
        result = self.processor.adjust_brightness(self.test_image, 1.5)
        self.assertIsInstance(result, Image.Image)
    
    def test_adjust_contrast(self):
        """Тест изменения контраста"""
        result = self.processor.adjust_contrast(self.test_image, 1.5)
        self.assertIsInstance(result, Image.Image)
    
    def test_resize_image(self):
        """Тест изменения размера"""
        result = self.processor.resize_image(self.test_image, 50, 50)
        self.assertEqual(result.size, (50, 50))

if __name__ == '__main__':
    unittest.main()
