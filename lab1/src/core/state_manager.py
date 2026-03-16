import json
import os
from typing import Any, Dict
from src.utils.exceptions import SaveError, LoadError

class StateManager:
    def __init__(self, filename: str = "data/kindergarten_state.json"):
        self.filename = filename
    
    def save(self, data: Dict[str, Any]) -> None:
        try:
            # Создаем папку, если её нет
            os.makedirs(os.path.dirname(self.filename), exist_ok=True)
            
            # Сохраняем
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            print(f" Состояние сохранено в {self.filename}")
            
        except Exception as e:
            raise SaveError(f"Ошибка сохранения: {e}")
    
    def load(self) -> Dict[str, Any]:
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Состояние загружено из {self.filename}")
            return data
            
        except FileNotFoundError:
            raise LoadError(f"Файл {self.filename} не найден")
        except json.JSONDecodeError as e:
            raise LoadError(f"Файл {self.filename} испорчен: {e}")
    
    def load_or_default(self, default: Dict[str, Any]) -> Dict[str, Any]:
        try:
            return self.load()
        except (LoadError):
            print("Создано новое состояние")
            return default