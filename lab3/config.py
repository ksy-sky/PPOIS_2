import yaml
import os

class Config:
    """Класс для загрузки и хранения конфигураций"""
    
    def __init__(self):
        self.settings = {}
        self.game_config = {}
        self.load_configs()
    
    def load_configs(self):
        """Загрузка всех конфигурационных файлов"""
        try:
            with open('configs/settings.yaml', 'r', encoding='utf-8') as f:
                self.settings = yaml.safe_load(f)
            
            with open('configs/game_config.yaml', 'r', encoding='utf-8') as f:
                self.game_config = yaml.safe_load(f)
        except FileNotFoundError as e:
            print(f"Ошибка: файл конфигурации не найден - {e}")
            raise
        except yaml.YAMLError as e:
            print(f"Ошибка: некорректный YAML - {e}")
            raise
    
    def get_screen_width(self):
        return self.settings['screen']['width']
    
    def get_screen_height(self):
        return self.settings['screen']['height']
    
    def get_cell_size(self):
        return self.game_config['board']['cell_size']
    
    def get_board_size(self):
        return self.game_config['board']['size']
    
    def get_color(self, color_name):
        return self.game_config['colors'][color_name]

# Глобальный экземпляр конфигурации
config = Config()