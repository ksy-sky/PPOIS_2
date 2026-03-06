from typing import List, Optional, Dict, Any
from src.models.child import Child
from src.models.teacher import Teacher
from src.models.parent import Parent
from src.models.group import Group
from src.models.teaching_material import TeachingMaterial
from src.models.educational_game import EducationalGame
from src.core.state_manager import StateManager
from src.utils.exceptions import ChildNotFoundError, ParentNotFoundError, GameNotFoundError, GroupError


class Kindergarten:
    
    def __init__(self, teacher_name: str = "Анна Петровна", state_file: str = "data/kindergarten_state.json"):
        self.state_manager = StateManager(state_file)
        self.teacher = Teacher(teacher_name)
        self.children: List[Child] = []
        self.parents: List[Parent] = []
        self.materials: List[TeachingMaterial] = []
        self.games: List[EducationalGame] = []
        self.groups: List[Group] = []
        # Загружаем состояние
        self._load_state()
        if not self.groups:
            self._create_default_groups()
    
    def _load_state(self) -> None:
        default = {
            "children": [],
            "parents": [],
            "materials": [],
            "games": [],
            "groups": []
        }
        
        data = self.state_manager.load_or_default(default)
        for child_data in data.get("children", []):
            self.children.append(Child.from_dict(child_data))
        for group_data in data.get("groups", []):
            group = Group.from_dict(group_data, self.children)
            self.groups.append(group)
        for mat_data in data.get("materials", []):
            self.materials.append(TeachingMaterial.from_dict(mat_data))
        for game_data in data.get("games", []):
            self.games.append(EducationalGame.from_dict(game_data))
        for parent_data in data.get("parents", []):
            child = self.get_child_by_name(parent_data.get("child_name", ""))
            if child:
                self.parents.append(Parent(parent_data["name"], child))
    
    def save_state(self) -> None:
        """Сохранить состояние в файл"""
        data = {
            "teacher": self.teacher.to_dict(),
            "children": [c.to_dict() for c in self.children],
            "parents": [p.to_dict() for p in self.parents],
            "materials": [m.to_dict() for m in self.materials],
            "games": [g.to_dict() for g in self.games],
            "groups": [g.to_dict() for g in self.groups]
        }
        self.state_manager.save(data)
    
    def _create_default_groups(self) -> None:
        """Создать стандартные группы"""
        for group_name in Group.GROUP_TYPES.keys():
            self.groups.append(Group(group_name))
        print(f"Созданы группы: {', '.join([g.name for g in self.groups])}")

    def get_all_children(self) -> List[Child]:
        return self.children.copy()
    
    def get_child_by_name(self, name: str) -> Optional[Child]:
        for child in self.children:
            if child.name.lower() == name.lower():
                return child
        return None
    
    def get_child_or_raise(self, name: str) -> Child:
        child = self.get_child_by_name(name)
        if not child:
            raise ChildNotFoundError(f"Ребенок '{name}' не найден")
        return child
    
    def get_parent_for_child(self, child: Child) -> Optional[Parent]:
        for parent in self.parents:
            if parent.child == child:
                return parent
        return None
    
    def get_parent_or_raise(self, child: Child) -> Parent:
        parent = self.get_parent_for_child(child)
        if not parent:
            raise ParentNotFoundError(f"У {child.name} нет родителя")
        return parent
    
    def get_game_by_name(self, name: str) -> Optional[EducationalGame]:
        for game in self.games:
            if game.name.lower() == name.lower():
                return game
        return None
    
    def get_game_or_raise(self, name: str) -> EducationalGame:
        game = self.get_game_by_name(name)
        if not game:
            raise GameNotFoundError(f"Игра '{name}' не найдена")
        return game
        
    def add_child(self, name: str, age: int) -> Child:
        child = Child(name, age)
        self.children.append(child)
        print(f"Добавлен ребенок: {child.name}")
        return child
        
    def add_parent(self, name: str, child: Child) -> Parent:
        if child not in self.children:
            raise ValueError(f"Ребенок {child.name} не найден в саду")
        
        parent = Parent(name, child)
        self.parents.append(parent)
        print(f"Добавлен родитель: {parent.name} для {child.name}")
        return parent
        
    def get_all_materials(self) -> List[TeachingMaterial]:
        return self.materials.copy()
    
    def add_material(self, title: str, quantity: int) -> TeachingMaterial:
        material = TeachingMaterial(title, quantity)
        self.materials.append(material)
        print(f"Добавлен материал: {title} ({quantity} шт.)")
        return material
        
    def get_all_games(self) -> List[EducationalGame]:
        return self.games.copy()
    
    def add_game(self, name: str, description: str, min_age: int, max_age: int) -> EducationalGame:
        game = EducationalGame(name, description, min_age, max_age)
        self.games.append(game)
        print(f"Добавлена игра: {name} (для {min_age}-{max_age} лет)")
        return game
    
    def get_games_for_child(self, child: Child) -> List[EducationalGame]:
        return [g for g in self.games if g.can_play(child.age)]
    
    def feed_child(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        return self.teacher.feed_child(child)
    
    def put_to_sleep(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        return self.teacher.put_to_sleep(child)
    
    def wake_up(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        return self.teacher.wake_up(child)
    
    def start_game(self, child_name: str, game_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        game = self.get_game_or_raise(game_name)
        
        game.check_age(child.name, child.age)
        
        return self.teacher.start_game(child, game.name)
    
    def finish_game(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        return self.teacher.finish_game(child)
    
    def drop_off_child(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        parent = self.get_parent_or_raise(child)
        return parent.drop_off()
    
    def pickup_child(self, child_name: str) -> Dict[str, Any]:
        child = self.get_child_or_raise(child_name)
        parent = self.get_parent_or_raise(child)
        return parent.pickup()
    
    def get_all_groups(self) -> List[Group]:
        return self.groups.copy()

    def get_group_by_name(self, name: str) -> Optional[Group]:
        for group in self.groups:
            if group.name.lower() == name.lower():
                return group
        return None

    def get_group_for_child(self, child: Child) -> Optional[Group]:
        for group in self.groups:
            if child in group.get_children():
                return group
        return None

    def assign_child_to_group(self, child_name: str, group_name: str) -> str:
        child = self.get_child_or_raise(child_name)
        group = self.get_group_by_name(group_name)
    
        if not group:
            raise GroupError(f"Группа '{group_name}' не найдена")
    
    # Убираем ребенка из текущей группы, если он там есть
        current_group = self.get_group_for_child(child)
        if current_group:
            current_group.remove_child(child)
    
    # Добавляем в новую группу
        group.add_child(child)
        return f"Ребенок {child.name} определен в группу '{group.name}'"

    def show_groups(self) -> str:
        """Показать все группы и детей в них"""
        result = "\nГРУППЫ ДЕТСКОГО САДА:\n" + "-"*40
        for group in self.groups:
            result += f"\n{group}"
            for child in group.get_children():
                result += f"\n  • {child}"
        return result 
    def organize_educational_process(self, game_name: str, group_name: Optional[str] = None) -> str:
        """
        Организация учебного процесса - проведение занятия
        """
        # Получаем игру
        game = self.get_game_or_raise(game_name)
        
        # Получаем детей (либо из конкретной группы, либо всех)
        children = []
        if group_name:
            group = self.get_group_by_name(group_name)
            if not group:
                return f"Группа '{group_name}' не найдена"
            children = group.get_children()
        else:
            # Берем всех детей, которые сейчас в саду (не "left")
            children = [c for c in self.children if c.state != "left"]
        
        if not children:
            return "Нет детей для проведения занятия"
        
        # Собираем словарь материалов
        materials_dict = {m.title: m for m in self.materials}
        
        # Проводим занятие
        result = self.teacher.conduct_lesson(children, game, materials_dict)
        
        return result["message"]
    
    def get_educational_report(self) -> str:
        lines = ["\n=== ОТЧЕТ ОБ УЧЕБНОМ ПРОЦЕССА ==="]
        
        # Дети по группам
        lines.append("\nДети по группам:")
        for group in self.groups:
            children_in_group = group.get_children()
            if children_in_group:
                lines.append(f"  {group.name}: {len(children_in_group)} детей")
                for child in children_in_group:
                    status = "в саду" if child.state != "left" else "дома"
                    lines.append(f"    • {child.name} ({child.age} лет) - {status}")
        
        # Доступные материалы
        lines.append("\nУчебные материалы:")
        for material in self.materials:
            lines.append(f"  • {material}")
        
        # Доступные игры
        lines.append("\nРазвивающие игры:")
        for game in self.games:
            lines.append(f"  • {game}")
        
        return "\n".join(lines)
