# src/models/educational_game.py
from typing import List, Optional
from src.utils.exceptions import GameAgeError, MaterialNotFoundError

class EducationalGame:
    def __init__(self, name: str, description: str, min_age: int, max_age: int, 
                 required_materials: List[str] = None):
        if min_age > max_age:
            raise ValueError("Минимальный возраст не может быть больше максимального")
        
        self.name = name
        self.description = description
        self.min_age = min_age
        self.max_age = max_age
        self.required_materials = required_materials or []  # список названий материалов
    
    def can_play(self, child_age: int) -> bool:
        return self.min_age <= child_age <= self.max_age
    
    def check_age(self, child_name: str, child_age: int) -> None:
        if not self.can_play(child_age):
            raise GameAgeError( 
                f"{child_name} ({child_age} лет) не может играть в '{self.name}' "
                f"(игра для {self.min_age}-{self.max_age} лет)"
            )
    
    def check_materials(self, available_materials: dict) -> List[str]:
        """Проверяет, есть ли все необходимые материалы"""
        missing = []
        for material_name in self.required_materials:
            if material_name not in available_materials:
                missing.append(material_name)
            elif available_materials[material_name].quantity <= 0:
                missing.append(f"{material_name} (закончились)")
        return missing

    def __str__(self) -> str:
        materials = f", нужно: {', '.join(self.required_materials)}" if self.required_materials else ""
        return f"{self.name} (для {self.min_age}-{self.max_age} лет): {self.description}{materials}"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "min_age": self.min_age,
            "max_age": self.max_age,
            "required_materials": self.required_materials
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EducationalGame":
        return cls(
            data["name"], 
            data["description"], 
            data["min_age"], 
            data["max_age"],
            data.get("required_materials", [])
        )