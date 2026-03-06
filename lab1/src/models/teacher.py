from typing import List, Dict, Any
from src.utils.exceptions import InvalidStateError, MaterialNotFoundError

class Teacher:
    def __init__(self, name: str):
        """Создание воспитателя"""
        self.name = name
    
    def _handle_result(self, success: bool, message: str, exception=None) -> dict:
        """Унифицированная обработка результатов"""
        if not success and exception:
            raise exception
        return {
            "success": success,
            "message": message
        }
    
    def feed_child(self, child) -> dict:
        """Покормить ребенка"""
        if child.state == "hungry":
            child.update_state("awake")
            return self._handle_result(
                True, 
                f"{self.name} покормил(а) {child.name}"
            )
        elif child.state == "left":
            return self._handle_result(
                False,
                f"{child.name} нет в саду",
                InvalidStateError(f"{child.name} нет в саду")
            )
        else:
            return self._handle_result(
                False,
                f"{child.name} не голоден",
                InvalidStateError(f"{child.name} не голоден (сейчас {child.state})")
            )
    
    def put_to_sleep(self, child) -> dict:
        """Уложить ребенка спать"""
        if child.state in ["awake", "playing"]:
            child.update_state("sleeping")
            return self._handle_result(
                True,
                f"{self.name} уложил(а) {child.name} спать"
            )
        elif child.state == "left":
            return self._handle_result(
                False,
                f"{child.name} нет в саду",
                InvalidStateError(f"{child.name} нет в саду")
            )
        else:
            return self._handle_result(
                False,
                f"{child.name} нельзя уложить (сейчас {child.state})",
                InvalidStateError(f"{child.name} нельзя уложить (сейчас {child.state})")
            )
            
    def finish_game(self, child) -> dict:
        """Закончить игру"""
        if child.state == "playing":
            child.update_state("hungry")
            return self._handle_result(
                True,
                f"{child.name} закончил игру и проголодался"
            )
        elif child.state == "left":
            return self._handle_result(
                False,
                f"{child.name} нет в саду",
                InvalidStateError(f"{child.name} нет в саду")
            )
        else:
            return self._handle_result(
                False,
                f"{child.name} не играет",
                InvalidStateError(f"{child.name} не играет (сейчас {child.state})")
            )

    def wake_up(self, child) -> dict:
        """Разбудить ребенка"""
        if child.state == "sleeping":
            child.update_state("awake")
            return self._handle_result(
                True,
                f"{self.name} разбудил(а) {child.name}"
            )
        elif child.state == "left":
            return self._handle_result(
                False,
                f"{child.name} нет в саду",
                InvalidStateError(f"{child.name} нет в саду")
            )
        else:
            return self._handle_result(
                False,
                f"{child.name} не спит",
                InvalidStateError(f"{child.name} не спит (сейчас {child.state})")
            )
    
    def start_game(self, child, game_name: str) -> dict:
        """Начать игру"""
        if child.state == "hungry":
            return self._handle_result(
                False,
                f"{child.name} голоден, сначала покормите!",
                InvalidStateError(f"{child.name} голоден, не может играть")
            )
        elif child.state == "awake":
            child.update_state("playing")
            return self._handle_result(
                True,
                f"{self.name} играет с {child.name} в {game_name}"
            )
        elif child.state == "left":
            return self._handle_result(
                False,
                f"{child.name} нет в саду",
                InvalidStateError(f"{child.name} нет в саду")
            )
        else:
            return self._handle_result(
                False,
                f"{child.name} не может играть (сейчас {child.state})",
                InvalidStateError(f"{child.name} не может играть (сейчас {child.state})")
            )
        
    def conduct_lesson(self, children: List, game, materials_dict: Dict) -> dict:
        # Проверяем наличие материалов
        missing = game.check_materials(materials_dict)
        if missing:
            return {
                "success": False,
                "message": f"Не хватает материалов для занятия '{game.name}': {', '.join(missing)}"
            }
        
        # Проверяем детей
        valid_children = []
        invalid_children = []
        
        for child in children:
            if child.state == "left":
                invalid_children.append(f"{child.name} (нет в саду)")
            elif child.state == "sleeping":
                invalid_children.append(f"{child.name} (спит)")
            elif child.state == "hungry":
                invalid_children.append(f"{child.name} (голоден)")
            elif not game.can_play(child.age):
                invalid_children.append(f"{child.name} (не подходит по возрасту)")
            else:
                valid_children.append(child)
        
        if not valid_children:
            return {
                "success": False,
                "message": f"Нет детей, готовых к занятию '{game.name}'"
            }
        
        # Используем материалы
        used_materials = []
        for material_name in game.required_materials:
            if material_name in materials_dict:
                materials_dict[material_name].use(1)
                used_materials.append(material_name)
        
        # Проводим занятие - все дети переходят в состояние "playing"
        for child in valid_children:
            child.update_state("playing")
        
        child_names = ", ".join([c.name for c in valid_children])
        
        return {
            "success": True,
            "message": f"{self.name} провел(а) занятие '{game.name}' с детьми: {child_names}. "
                      f"Использованы материалы: {', '.join(used_materials)}",
            "children": valid_children,
            "materials_used": used_materials
        }

    def to_dict(self) -> dict:
        return {"name": self.name}
    
    @classmethod
    def from_dict(cls, data: dict) -> "Teacher":
        """Загрузка из словаря"""
        return cls(data["name"])