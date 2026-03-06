from typing import List
from src.models.child import Child
from src.utils.exceptions import GroupError, InvalidAgeError

class Group:
    GROUP_TYPES = {
        "ясли": (1, 2),
        "младшая": (3, 4),
        "средняя": (4, 5),
        "старшая": (5, 6),
        "подготовительная": (6, 7)
    }
    
    def __init__(self, name: str):
        if name not in self.GROUP_TYPES:
            raise GroupError(f"Неизвестный тип группы: {name}. Допустимые: {list(self.GROUP_TYPES.keys())}")
        
        self.name = name
        self.min_age, self.max_age = self.GROUP_TYPES[name]
        self.children: List[Child] = []
        self.capacity = 15  # максимум детей в группе (можно менять)
    
    def add_child(self, child: Child) -> None:
        # Проверяем возраст
        if child.age < self.min_age or child.age > self.max_age:
            raise GroupError(
                f"Ребенок {child.name} ({child.age} лет) не подходит в группу '{self.name}' "
                f"(возраст {self.min_age}-{self.max_age} лет)"
            )
        
        # Проверяем, есть ли уже ребенок в группе
        if child in self.children:
            raise GroupError(f"Ребенок {child.name} уже в группе '{self.name}'")
        
        # Проверяем вместимость
        if len(self.children) >= self.capacity:
            raise GroupError(f"Группа '{self.name}' переполнена (максимум {self.capacity} детей)"
                f"Нельзя добавить ребенка {child.name}"
            )
        
        self.children.append(child)
        print(f"  Ребенок {child.name} добавлен в группу '{self.name}'")
    
    def remove_child(self, child: Child) -> None:
        if child in self.children:
            self.children.remove(child)
            print(f"  Ребенок {child.name} убран из группы '{self.name}'")
    
    def get_children(self) -> List[Child]:
        return self.children.copy()
    
    def get_count(self) -> int:
        return len(self.children)
    
    def has_place(self) -> bool:
        return len(self.children) < self.capacity
    
    def __str__(self) -> str:
        return f"Группа '{self.name}' ({self.min_age}-{self.max_age} лет): {len(self.children)}/{self.capacity}"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "children": [child.name for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: dict, all_children: List[Child]) -> "Group":
        """Создать группу из словаря"""
        group = cls(data["name"])
        # Восстанавливаем детей по именам
        for child_name in data.get("children", []):
            for child in all_children:
                if child.name == child_name:
                    group.children.append(child)
                    break
        return group