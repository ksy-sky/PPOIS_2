#!/usr/bin/env python3
import pytest
import tempfile
import os
import json
from typing import List, Optional, Dict, Any
from unittest.mock import MagicMock, patch
from src.interfaces.cli_interface import CLIInterface
from src.core.kindergarten import Kindergarten
from src.models.child import Child
from src.models.teacher import Teacher
from src.models.parent import Parent
from src.models.group import Group
from src.models.teaching_material import TeachingMaterial
from src.models.educational_game import EducationalGame
from src.core.state_manager import StateManager
from src.utils.exceptions import (
    KindergartenException, ChildNotFoundError,
    ParentNotFoundError, GameNotFoundError, GroupError,
    MaterialNotFoundError, InvalidStateError,
    GameAgeError, SaveError, LoadError, InvalidAgeError 
)

class TestChild:
    """Тесты для класса Child"""
    
    def test_create_child_valid(self):
        """Тест создания ребенка с валидными данными"""
        child = Child("Маша", 4)
        assert child.name == "Маша"
        assert child.age == 4
        assert child.state == "left"  # состояние по умолчанию
    
    def test_create_child_with_custom_state(self):
        """Тест создания ребенка с указанием состояния"""
        child = Child("Петя", 5, initial_state="awake")
        assert child.state == "awake"
    
    def test_create_child_invalid_age_low(self):
        """Тест создания ребенка с слишком маленьким возрастом"""
        with pytest.raises(InvalidAgeError) as exc_info:
            Child("Малыш", 0)
        assert "недопустим для детского сада" in str(exc_info.value)
    
    def test_create_child_invalid_age_high(self):
        """Тест создания ребенка с слишком большим возрастом"""
        with pytest.raises(InvalidAgeError) as exc_info:
            Child("Школьник", 8)
        assert "недопустим для детского сада" in str(exc_info.value)
    
    def test_create_child_invalid_state(self):
        """Тест создания ребенка с недопустимым состоянием"""
        with pytest.raises(InvalidStateError) as exc_info:
            Child("Маша", 4, initial_state="flying")
        assert "Недопустимое состояние" in str(exc_info.value)
    
    def test_create_child_invalid_name_type(self):
        """Тест создания ребенка с неверным типом имени"""
        with pytest.raises(TypeError):
            Child(123, 4)
    
    def test_create_child_invalid_age_type(self):
        """Тест создания ребенка с неверным типом возраста"""
        with pytest.raises(TypeError):
            Child("Маша", "четыре")
    
    def test_update_state_valid(self):
        """Тест изменения состояния на валидное"""
        child = Child("Маша", 4)
        child.update_state("awake")
        assert child.state == "awake"
        child.update_state("hungry")
        assert child.state == "hungry"
        child.update_state("playing")
        assert child.state == "playing"
        child.update_state("sleeping")
        assert child.state == "sleeping"
    
    def test_update_state_invalid(self):
        """Тест изменения состояния на невалидное"""
        child = Child("Маша", 4)
        with pytest.raises(InvalidStateError):
            child.update_state("crying")
    
    def test_state_property(self):
        """Тест property state"""
        child = Child("Маша", 4, initial_state="hungry")
        assert child.state == "hungry"
        
        # Пытаемся изменить напрямую (не должно работать с property)
        with pytest.raises(AttributeError):
            child.state = "awake"
    
    def test_make_hungry_valid(self):
        """Тест make_hungry из валидных состояний"""
        test_cases = ["awake", "playing"]
        for initial_state in test_cases:
            child = Child("Маша", 4, initial_state=initial_state)
            result = child.make_hungry()
            assert result is True
            assert child.state == "hungry"
    
    def test_make_hungry_invalid(self):
        """Тест make_hungry из невалидных состояний"""
        test_cases = ["hungry", "sleeping", "left"]
        for initial_state in test_cases:
            child = Child("Маша", 4, initial_state=initial_state)
            with pytest.raises(InvalidStateError):
                child.make_hungry()
    
    def test_str_representation(self):
        """Тест строкового представления"""
        child = Child("Маша", 4, initial_state="playing")
        assert str(child) == "Маша (4 лет) - playing"
    
    def test_to_dict(self):
        """Тест сериализации в словарь"""
        child = Child("Маша", 4, initial_state="hungry")
        data = child.to_dict()
        assert data == {"name": "Маша", "age": 4, "state": "hungry"}
    
    def test_from_dict(self):
        """Тест десериализации из словаря"""
        data = {"name": "Петя", "age": 5, "state": "awake"}
        child = Child.from_dict(data)
        assert child.name == "Петя"
        assert child.age == 5
        assert child.state == "awake"
    
    def test_from_dict_invalid_age(self):
        """Тест десериализации с невалидным возрастом"""
        data = {"name": "Петя", "age": 10, "state": "awake"}
        with pytest.raises(InvalidAgeError):
            Child.from_dict(data)
    
    @pytest.mark.parametrize("age,expected", [
        (1, True), (2, True), (3, True), (4, True), 
        (5, True), (6, True), (7, True), (0, False), (8, False)
    ])
    def test_age_validation_edge_cases(self, age, expected):
        """Параметризованный тест граничных значений возраста"""
        if expected:
            child = Child("Тест", age)
            assert child.age == age
        else:
            with pytest.raises(InvalidAgeError):
                Child("Тест", age)

class TestTeacher:
    """Тесты для класса Teacher"""
    
    @pytest.fixture
    def teacher(self):
        """Фикстура воспитателя"""
        return Teacher("Анна Петровна")
    
    @pytest.fixture
    def hungry_child(self):
        """Фикстура голодного ребенка"""
        return Child("Маша", 4, initial_state="hungry")
    
    @pytest.fixture
    def awake_child(self):
        """Фикстура бодрствующего ребенка"""
        return Child("Петя", 5, initial_state="awake")
    
    @pytest.fixture
    def playing_child(self):
        """Фикстура играющего ребенка"""
        return Child("Даша", 3, initial_state="playing")
    
    @pytest.fixture
    def sleeping_child(self):
        """Фикстура спящего ребенка"""
        return Child("Вася", 4, initial_state="sleeping")
    
    @pytest.fixture
    def left_child(self):
        """Фикстура ребенка дома"""
        return Child("Катя", 4, initial_state="left")
    
    def test_teacher_creation(self, teacher):
        """Тест создания воспитателя"""
        assert teacher.name == "Анна Петровна"
    
    def test_feed_child_success(self, teacher, hungry_child):
        """Тест успешного кормления голодного ребенка"""
        result = teacher.feed_child(hungry_child)
        assert result["success"] is True
        assert "покормил(а) Маша" in result["message"]
        assert hungry_child.state == "awake"
    
    def test_feed_child_not_hungry(self, teacher, awake_child):
        """Тест кормления неголодного ребенка"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.feed_child(awake_child)
        assert "не голоден" in str(exc_info.value)
    
    def test_feed_child_left(self, teacher, left_child):
        """Тест кормления ребенка, которого нет в саду"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.feed_child(left_child)
        assert "нет в саду" in str(exc_info.value)
    
    def test_put_to_sleep_from_awake(self, teacher, awake_child):
        """Тест укладывания бодрствующего ребенка"""
        result = teacher.put_to_sleep(awake_child)
        assert result["success"] is True
        assert "уложил(а) Петя спать" in result["message"]
        assert awake_child.state == "sleeping"
    
    def test_put_to_sleep_from_playing(self, teacher, playing_child):
        """Тест укладывания играющего ребенка"""
        result = teacher.put_to_sleep(playing_child)
        assert result["success"] is True
        assert "уложил(а) Даша спать" in result["message"]
        assert playing_child.state == "sleeping"
    
    def test_put_to_sleep_from_sleeping(self, teacher, sleeping_child):
        """Тест укладывания спящего ребенка"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.put_to_sleep(sleeping_child)
        assert "нельзя уложить" in str(exc_info.value)
    
    def test_put_to_sleep_left(self, teacher, left_child):
        """Тест укладывания ребенка, которого нет в саду"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.put_to_sleep(left_child)
        assert "нет в саду" in str(exc_info.value)
    
    def test_wake_up_success(self, teacher, sleeping_child):
        """Тест успешного пробуждения"""
        result = teacher.wake_up(sleeping_child)
        assert result["success"] is True
        assert "разбудил(а) Вася" in result["message"]
        assert sleeping_child.state == "awake"
    
    def test_wake_up_not_sleeping(self, teacher, awake_child):
        """Тест пробуждения неспящего ребенка"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.wake_up(awake_child)
        assert "не спит" in str(exc_info.value)
    
    def test_wake_up_left(self, teacher, left_child):
        """Тест пробуждения ребенка, которого нет в саду"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.wake_up(left_child)
        assert "нет в саду" in str(exc_info.value)
    
    def test_start_game_success(self, teacher, awake_child):
        """Тест успешного начала игры"""
        result = teacher.start_game(awake_child, "Лото")
        assert result["success"] is True
        assert "играет с Петя в Лото" in result["message"]
        assert awake_child.state == "playing"
    
    def test_start_game_hungry(self, teacher, hungry_child):
        """Тест начала игры голодным ребенком"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.start_game(hungry_child, "Лото")
        assert "голоден" in str(exc_info.value)
    
    def test_start_game_sleeping(self, teacher, sleeping_child):
        """Тест начала игры спящим ребенком"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.start_game(sleeping_child, "Лото")
        assert "не может играть" in str(exc_info.value)
    
    def test_start_game_left(self, teacher, left_child):
        """Тест начала игры с ребенком, которого нет в саду"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.start_game(left_child, "Лото")
        assert "нет в саду" in str(exc_info.value)
    
    def test_finish_game_success(self, teacher, playing_child):
        """Тест успешного завершения игры"""
        result = teacher.finish_game(playing_child)
        assert result["success"] is True
        assert "закончил игру и проголодался" in result["message"]
        assert playing_child.state == "hungry"
    
    def test_finish_game_not_playing(self, teacher, awake_child):
        """Тест завершения игры неиграющим ребенком"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.finish_game(awake_child)
        assert "не играет" in str(exc_info.value)
    
    def test_finish_game_left(self, teacher, left_child):
        """Тест завершения игры с ребенком, которого нет в саду"""
        with pytest.raises(InvalidStateError) as exc_info:
            teacher.finish_game(left_child)
        assert "нет в саду" in str(exc_info.value)
    
    def test_to_dict(self, teacher):
        """Тест сериализации в словарь"""
        data = teacher.to_dict()
        assert data == {"name": "Анна Петровна"}
    
    def test_from_dict(self):
        """Тест десериализации из словаря"""
        data = {"name": "Мария Ивановна"}
        teacher = Teacher.from_dict(data)
        assert teacher.name == "Мария Ивановна"

    def test_conduct_lesson_success(self, teacher, awake_child, playing_child):
        """Тест успешного проведения занятия с группой детей"""
        # Создаем игру с материалами
        game = EducationalGame("Рисование", "Учимся рисовать", 3, 6, ["Краски", "Кисточки"])
        
        # Создаем словарь материалов (ОБЪЕКТЫ, а не числа)
        materials = {
            "Краски": TeachingMaterial("Краски", 10),
            "Кисточки": TeachingMaterial("Кисточки", 5),
            "Бумага": TeachingMaterial("Бумага", 20)
        }
        
        # Подготавливаем детей
        child1 = awake_child  # Петя, 5 лет, awake
        child2 = playing_child  # Даша, 3 года, playing
        child3 = Child("Вася", 4, initial_state="awake")
        children = [child1, child2, child3]
        
        # Проводим занятие
        result = teacher.conduct_lesson(children, game, materials)
        
        # Проверяем результат
        assert result["success"] is True
        assert "провел(а) занятие 'Рисование'" in result["message"]
        assert "Использованы материалы: Краски, Кисточки" in result["message"]
        assert len(result["children"]) == 3
        
        # Проверяем, что материалы использованы
        assert materials["Краски"].quantity == 9  # было 10, стало 9
        assert materials["Кисточки"].quantity == 4  # было 5, стало 4
        assert materials["Бумага"].quantity == 20  # не использовалась
        
        # Проверяем, что дети перешли в состояние playing
        assert child1.state == "playing"
        assert child2.state == "playing"
        assert child3.state == "playing"

    def test_conduct_lesson_missing_materials(self, teacher, awake_child):
        """Тест проведения занятия с отсутствующими материалами"""
        game = EducationalGame("Рисование", "Учимся рисовать", 3, 6, ["Краски", "Кисточки", "Фломастеры"])
        
        # Создаем материалы как ОБЪЕКТЫ
        materials = {
            "Краски": TeachingMaterial("Краски", 10),
            "Кисточки": TeachingMaterial("Кисточки", 0)  # закончились (quantity = 0)
            # "Фломастеры" вообще нет
        }
        
        children = [awake_child]
        
        result = teacher.conduct_lesson(children, game, materials)
        
        assert result["success"] is False
        assert "Не хватает материалов" in result["message"]
        # Проверяем, что в сообщении есть оба недостающих материала
        assert "Кисточки (закончились)" in result["message"] or "Кисточки" in result["message"]
        assert "Фломастеры" in result["message"]

    def test_conduct_lesson_no_children(self, teacher):
        """Тест проведения занятия без детей"""
        game = EducationalGame("Рисование", "Учимся рисовать", 3, 6, ["Краски"])
        materials = {"Краски": TeachingMaterial("Краски", 10)}
        
        result = teacher.conduct_lesson([], game, materials)
        
        assert result["success"] is False
        assert "Нет детей, готовых к занятию" in result["message"]

    def test_conduct_lesson_all_children_invalid(self, teacher):
        """Тест проведения занятия, когда все дети не могут участвовать"""
        game = EducationalGame("Рисование", "Учимся рисовать", 3, 6, ["Краски"])
        materials = {"Краски": TeachingMaterial("Краски", 10)}
        
        # Создаем детей, которые НЕ могут участвовать
        child1 = Child("Соня", 4, initial_state="sleeping")  # спит
        child2 = Child("Дима", 2, initial_state="awake")     # маленький возраст
        child3 = Child("Лена", 7, initial_state="hungry")    # голодная и большой возраст
        
        children = [child1, child2, child3]
        
        result = teacher.conduct_lesson(children, game, materials)
        
        assert result["success"] is False
        assert "Нет детей, готовых к занятию" in result["message"]

    def test_conduct_lesson_filter_invalid_children(self, teacher, awake_child):
        """Тест фильтрации детей - часть может, часть нет"""
        game = EducationalGame("Рисование", "Учимся рисовать", 3, 6, ["Краски"])
        materials = {"Краски": TeachingMaterial("Краски", 10)}
        
        # Валидные дети
        child1 = awake_child  # Петя, 5 лет, awake - может
        
        # Невалидные дети
        child2 = Child("Соня", 4, initial_state="sleeping")   # спит
        child3 = Child("Дима", 2, initial_state="awake")      # маленький
        child4 = Child("Лена", 4, initial_state="left")       # дома
        child5 = Child("Коля", 4, initial_state="hungry")     # голодный
        
        children = [child1, child2, child3, child4, child5]
        
        result = teacher.conduct_lesson(children, game, materials)
        
        assert result["success"] is True
        assert "провел(а) занятие" in result["message"]
        assert len(result["children"]) == 1  # только Петя
        assert result["children"][0].name == "Петя"
        
        # Проверяем, что материалы использованы
        assert materials["Краски"].quantity == 9

    def test_conduct_lesson_different_age_groups(self, teacher):
        """Тест проведения занятия для детей разного возраста"""
        game = EducationalGame("Лего", "Конструирование", 4, 6, ["Кубики"])
        materials = {"Кубики": TeachingMaterial("Кубики", 20)}
        
        # Дети разного возраста
        children = [
            Child("Аня", 3, initial_state="awake"),  # слишком маленькая
            Child("Боря", 4, initial_state="awake"),  # подходит
            Child("Вова", 5, initial_state="awake"),  # подходит
            Child("Галя", 6, initial_state="awake"),  # подходит
            Child("Дима", 7, initial_state="awake")   # слишком большой
        ]
        
        result = teacher.conduct_lesson(children, game, materials)
        
        assert result["success"] is True
        assert len(result["children"]) == 3  # Боря, Вова, Галя
        # Проверяем имена детей в результате
        child_names = [c.name for c in result["children"]]
        assert "Боря" in child_names
        assert "Вова" in child_names
        assert "Галя" in child_names
        assert "Аня" not in child_names
        assert "Дима" not in child_names

    def test_conduct_lesson_game_without_materials(self, teacher, awake_child):
        """Тест проведения занятия, которое не требует материалов"""
        game = EducationalGame("Лото", "Настольная игра", 3, 6, [])  # без материалов
        materials = {}
        
        children = [awake_child]
        
        result = teacher.conduct_lesson(children, game, materials)
        
        assert result["success"] is True
        assert "провел(а) занятие 'Лото'" in result["message"]
        assert "Использованы материалы:" in result["message"]

    def test_conduct_lesson_multiple_uses_same_material(self, teacher):
        """Тест многократного использования одного материала"""
        game = EducationalGame("Кубики", "Строим башню", 3, 6, ["Кубики"])
        materials = {"Кубики": TeachingMaterial("Кубики", 5)}
        
        # Проводим занятие несколько раз
        children1 = [Child("Аня", 4, initial_state="awake")]
        children2 = [Child("Боря", 4, initial_state="awake")]
        
        result1 = teacher.conduct_lesson(children1, game, materials)
        assert result1["success"] is True
        assert materials["Кубики"].quantity == 4
        
        result2 = teacher.conduct_lesson(children2, game, materials)
        assert result2["success"] is True
        assert materials["Кубики"].quantity == 3

    def test_conduct_lesson_material_runs_out(self, teacher):
        """Тест ситуации, когда материал заканчивается во время занятия"""
        game = EducationalGame("Кубики", "Строим башню", 3, 6, ["Кубики"])
        materials = {"Кубики": TeachingMaterial("Кубики", 1)}  # всего 1 кубик
        
        children = [
            Child("Аня", 4, initial_state="awake"),
            Child("Боря", 4, initial_state="awake")
        ]
        
        # Первое занятие - должно пройти
        result1 = teacher.conduct_lesson(children[:1], game, materials)
        assert result1["success"] is True
        assert materials["Кубики"].quantity == 0
        game2 = EducationalGame("Кубики", "Строим башню", 3, 6, ["Кубики"])
        materials2 = {"Кубики": TeachingMaterial("Кубики", 0)}  # уже закончились
        
        result2 = teacher.conduct_lesson(children[1:2], game2, materials2)
        assert result2["success"] is False
        assert "Не хватает материалов" in result2["message"]
        assert "Кубики (закончились)" in result2["message"]
    def test_conduct_lesson_check_materials_called(self, teacher, awake_child):
        """Тест, что check_materials вызывается правильно"""
        game = EducationalGame("Тест", "Описание", 3, 6, ["Материал1"])
        materials = {"Материал1": TeachingMaterial("Материал1", 5)}
        children = [awake_child]
        
        with patch.object(game, 'check_materials', return_value=[]) as mock_check:
            teacher.conduct_lesson(children, game, materials)
            mock_check.assert_called_once_with(materials)

    def test_conduct_lesson_all_invalid_reasons(self, teacher):
        """Тест всех причин, по которым ребенок не может участвовать"""
        game = EducationalGame("Тест", "Описание", 3, 6, [])
        materials = {}
        
        children = [
            Child("Левша", 4, initial_state="left"),      # нет в саду
            Child("Соня", 4, initial_state="sleeping"),   # спит
            Child("Голодный", 4, initial_state="hungry"), # голоден
            Child("Малыш", 2, initial_state="awake"),     # маленький возраст
            Child("Взрослый", 7, initial_state="awake")   # большой возраст
        ]
        
        result = teacher.conduct_lesson(children, game, materials)
        assert result["success"] is False
        assert "Нет детей, готовых к занятию" in result["message"]

    def test_conduct_lesson_with_valid_children(self, teacher):
        """Тест, что valid_children правильно заполняется"""
        game = EducationalGame("Тест", "Описание", 3, 6, [])
        materials = {}
        
        children = [
            Child("Петя", 4, initial_state="awake"),      # валидный
            Child("Левша", 4, initial_state="left"),      # невалидный
            Child("Маша", 5, initial_state="playing")     # валидный (playing тоже ок)
        ]
        
        result = teacher.conduct_lesson(children, game, materials)
        assert result["success"] is True
        assert len(result["children"]) == 2
        assert result["children"][0].name == "Петя"
        assert result["children"][1].name == "Маша"

class TestParent:
    """Тесты для класса Parent"""
    
    @pytest.fixture
    def child(self):
        """Фикстура ребенка"""
        return Child("Маша", 4, initial_state="left")
    
    @pytest.fixture
    def parent(self, child):
        """Фикстура родителя"""
        return Parent("Ольга", child)
    
    def test_parent_creation(self, parent, child):
        """Тест создания родителя"""
        assert parent.name == "Ольга"
        assert parent.child == child
    
    def test_drop_off_success(self, parent, child):
        """Тест успешного приведения ребенка"""
        assert child.state == "left"
        result = parent.drop_off()
        assert result["success"] is True
        assert "привел(а) Маша в сад" in result["message"]
        assert child.state == "hungry"
    
    def test_drop_off_already_in_kindergarten(self, parent, child):
        """Тест приведения ребенка, который уже в саду"""
        child.update_state("awake")
        with pytest.raises(InvalidStateError) as exc_info:
            parent.drop_off()
        assert "уже в саду" in str(exc_info.value)
    
    def test_pickup_success(self, parent, child):
        """Тест успешного забирания ребенка"""
        # Сначала приводим
        parent.drop_off()
        assert child.state != "left"
        
        # Забираем
        result = parent.pickup()
        assert result["success"] is True
        assert "забрал(а) Маша домой" in result["message"]
        assert child.state == "left"
    
    def test_pickup_already_home(self, parent, child):
        """Тест забирания ребенка, который уже дома"""
        assert child.state == "left"
        with pytest.raises(InvalidStateError) as exc_info:
            parent.pickup()
        assert "уже дома" in str(exc_info.value)
    
    def test_to_dict(self, parent, child):
        """Тест сериализации в словарь"""
        data = parent.to_dict()
        assert data == {"name": "Ольга", "child_name": "Маша"}
    
    def test_from_dict(self, child):
        """Тест десериализации из словаря"""
        data = {"name": "Иван", "child_name": "Маша"}
        parent = Parent.from_dict(data, child)
        assert parent.name == "Иван"
        assert parent.child == child

class TestGroup:
    """Тесты для класса Group"""
    
    @pytest.fixture
    def nursery_group(self):
        """Фикстура ясельной группы"""
        return Group("ясли")
    
    @pytest.fixture
    def junior_group(self):
        """Фикстура младшей группы"""
        return Group("младшая")
    
    @pytest.fixture
    def children(self):
        """Фикстура детей разного возраста"""
        return [
            Child("Малыш", 1),
            Child("Тоддлер", 2),
            Child("Дошкольник", 3),
            Child("Ребенок", 4),
            Child("Старший", 5),
            Child("Подготовишка", 6)
        ]
    
    def test_group_creation_valid(self):
        """Тест создания валидной группы"""
        for group_name in Group.GROUP_TYPES.keys():
            group = Group(group_name)
            assert group.name == group_name
            assert group.min_age == Group.GROUP_TYPES[group_name][0]
            assert group.max_age == Group.GROUP_TYPES[group_name][1]
            assert group.capacity == 15
            assert len(group.children) == 0
    
    def test_group_creation_invalid(self):
        """Тест создания невалидной группы"""
        with pytest.raises(GroupError) as exc_info:
            Group("несуществующая")
        assert "Неизвестный тип группы" in str(exc_info.value)
    
    def test_add_child_valid_age(self, nursery_group, children):
        """Тест добавления ребенка подходящего возраста"""
        child = children[0]  # 1 год
        nursery_group.add_child(child)
        assert child in nursery_group.get_children()
        assert nursery_group.get_count() == 1
    
    def test_add_child_invalid_age(self, nursery_group, children):
        """Тест добавления ребенка неподходящего возраста"""
        child = children[2]  # 3 года (слишком для яслей)
        with pytest.raises(GroupError) as exc_info:
            nursery_group.add_child(child)
        assert "не подходит в группу" in str(exc_info.value)
        assert nursery_group.get_count() == 0
    
    def test_add_child_duplicate(self, nursery_group, children):
        """Тест добавления ребенка, который уже в группе"""
        child = children[0]
        nursery_group.add_child(child)
        
        with pytest.raises(GroupError) as exc_info:
            nursery_group.add_child(child)
        assert "уже в группе" in str(exc_info.value)
        assert nursery_group.get_count() == 1
    
    def test_remove_child(self, nursery_group, children):
        """Тест удаления ребенка из группы"""
        child = children[0]
        nursery_group.add_child(child)
        assert nursery_group.get_count() == 1
        
        nursery_group.remove_child(child)
        assert nursery_group.get_count() == 0
        assert child not in nursery_group.get_children()
    
    def test_remove_child_not_in_group(self, nursery_group, children):
        """Тест удаления ребенка, которого нет в группе"""
        child = children[0]
        # Удаляем без добавления (просто не должно быть ошибки)
        nursery_group.remove_child(child)  # ничего не происходит
        assert nursery_group.get_count() == 0
    
    def test_get_children_copy(self, nursery_group, children):
        """Тест получения копии списка детей"""
        child = children[0]
        nursery_group.add_child(child)
        
        children_copy = nursery_group.get_children()
        assert children_copy == [child]
        
        # Изменение копии не должно влиять на оригинал
        children_copy.clear()
        assert nursery_group.get_count() == 1
    
    def test_has_place(self, nursery_group, children):
        """Тест проверки наличия места"""
        nursery_group.capacity = 2
        assert nursery_group.has_place() is True
        
        nursery_group.add_child(children[0])
        assert nursery_group.has_place() is True
        
        nursery_group.add_child(children[1])
        assert nursery_group.has_place() is False
    
    def test_str_representation(self, nursery_group, children):
        """Тест строкового представления"""
        assert str(nursery_group) == "Группа 'ясли' (1-2 лет): 0/15"
        
        nursery_group.add_child(children[0])
        assert str(nursery_group) == "Группа 'ясли' (1-2 лет): 1/15"
    
    def test_to_dict(self, nursery_group, children):
        """Тест сериализации в словарь"""
        child = children[0]
        nursery_group.add_child(child)
        
        data = nursery_group.to_dict()
        assert data["name"] == "ясли"
        assert child.name in data["children"]
    
    def test_from_dict(self, children):
        """Тест десериализации из словаря"""
        data = {
            "name": "младшая",
            "children": ["Малыш", "Тоддлер"]
        }
        
        group = Group.from_dict(data, children[:2])
        assert group.name == "младшая"
        assert len(group.children) == 2
        assert group.children[0].name == "Малыш"
        assert group.children[1].name == "Тоддлер"
    
    def test_from_dict_with_missing_child(self, children):
        """Тест десериализации с отсутствующим ребенком"""
        data = {
            "name": "младшая",
            "children": ["Малыш", "Неизвестный"]
        }
        
        group = Group.from_dict(data, children[:1])
        assert len(group.children) == 1  # Только найденный ребенок
        assert group.children[0].name == "Малыш"

class TestTeachingMaterial:
    """Тесты для класса TeachingMaterial"""
    
    def test_create_material_valid(self):
        """Тест создания материала с валидными данными"""
        material = TeachingMaterial("Кубики", 10)
        assert material.title == "Кубики"
        assert material.quantity == 10
    
    def test_create_material_negative_quantity(self):
        """Тест создания материала с отрицательным количеством"""
        with pytest.raises(ValueError) as exc_info:
            TeachingMaterial("Кубики", -5)
        assert "Количество не может быть отрицательным" in str(exc_info.value)
    
    def test_use_material_success(self):
        """Тест успешного использования материала"""
        material = TeachingMaterial("Краски", 5)
        material.use(3)
        assert material.quantity == 2
    
    def test_use_material_default_amount(self):
        """Тест использования материала с количеством по умолчанию"""
        material = TeachingMaterial("Пластилин", 5)
        material.use()  # используем 1 по умолчанию
        assert material.quantity == 4
    
    def test_use_material_not_enough(self):
        """Тест использования материала при нехватке"""
        material = TeachingMaterial("Кубики", 2)
        with pytest.raises(ValueError) as exc_info:
            material.use(5)
        assert "Не хватает Кубики" in str(exc_info.value)
        assert material.quantity == 2  # количество не изменилось
    
    def test_use_material_exact_amount(self):
        """Тест использования материала точно до нуля"""
        material = TeachingMaterial("Кубики", 3)
        material.use(3)
        assert material.quantity == 0
    
    def test_str_representation(self):
        """Тест строкового представления"""
        material = TeachingMaterial("Краски", 5)
        assert str(material) == "Краски (осталось: 5)"
        
        material.use(3)
        assert str(material) == "Краски (осталось: 2)"
    
    def test_to_dict(self):
        """Тест сериализации в словарь"""
        material = TeachingMaterial("Пластилин", 8)
        data = material.to_dict()
        assert data == {"title": "Пластилин", "quantity": 8}
    
    def test_from_dict(self):
        """Тест десериализации из словаря"""
        data = {"title": "Кубики", "quantity": 15}
        material = TeachingMaterial.from_dict(data)
        assert material.title == "Кубики"
        assert material.quantity == 15
    
    def test_from_dict_invalid_quantity(self):
        """Тест десериализации с невалидным количеством"""
        data = {"title": "Кубики", "quantity": -5}
        with pytest.raises(ValueError):
            TeachingMaterial.from_dict(data)

class TestEducationalGame:
    """Тесты для класса EducationalGame"""
    
    def test_create_game_valid(self):
        """Тест создания игры с валидными данными"""
        game = EducationalGame("Лото", "Классическое лото", 3, 6)
        assert game.name == "Лото"
        assert game.description == "Классическое лото"
        assert game.min_age == 3
        assert game.max_age == 6
    
    def test_create_game_invalid_age_range(self):
        """Тест создания игры с неверным возрастным диапазоном"""
        with pytest.raises(ValueError) as exc_info:
            EducationalGame("Лото", "Описание", 6, 3)
        assert "Минимальный возраст не может быть больше максимального" in str(exc_info.value)
    
    def test_can_play(self):
        """Тест проверки возможности игры"""
        game = EducationalGame("Пазлы", "Собираем картинку", 3, 5)
        
        assert game.can_play(3) is True
        assert game.can_play(4) is True
        assert game.can_play(5) is True
        assert game.can_play(2) is False
        assert game.can_play(6) is False
    
    @pytest.mark.parametrize("age,expected", [
        (3, True), (4, True), (5, True), (2, False), (6, False)
    ])
    def test_can_play_parametrized(self, age, expected):
        """Параметризованный тест can_play"""
        game = EducationalGame("Мозаика", "Описание", 3, 5)
        assert game.can_play(age) == expected
    
    def test_check_age_valid(self):
        """Тест проверки возраста (валидный случай)"""
        game = EducationalGame("Лото", "Описание", 3, 6)
        # Не должно быть исключения
        game.check_age("Маша", 4)
    
    def test_check_age_invalid_low(self):
        """Тест проверки возраста (слишком маленький)"""
        game = EducationalGame("Лото", "Описание", 3, 6)
        with pytest.raises(GameAgeError) as exc_info:
            game.check_age("Маша", 2)
        assert "Маша (2 лет) не может играть в 'Лото'" in str(exc_info.value)
        assert "игра для 3-6 лет" in str(exc_info.value)
    
    def test_check_age_invalid_high(self):
        """Тест проверки возраста (слишком большой)"""
        game = EducationalGame("Лото", "Описание", 3, 6)
        with pytest.raises(GameAgeError) as exc_info:
            game.check_age("Петя", 7)
        assert "Петя (7 лет) не может играть в 'Лото'" in str(exc_info.value)
    
    def test_str_representation(self):
        """Тест строкового представления"""
        game = EducationalGame("Лото", "Классическое лото с картинками", 3, 6)
        expected = "Лото (для 3-6 лет): Классическое лото с картинками"
        assert str(game) == expected
    
# tests/test_kindergarden.py - исправленный тест

    def test_to_dict(self):
        """Тест сериализации в словарь"""
        game = EducationalGame("Мозаика", "Собираем узоры", 4, 7, ["Кубики", "Краски"])
        data = game.to_dict()
        assert data == {
            "name": "Мозаика",
            "description": "Собираем узоры",
            "min_age": 4,
            "max_age": 7,
            "required_materials": ["Кубики", "Краски"]  # добавили это поле
        }

    def test_to_dict_without_materials(self):
        """Тест сериализации игры без материалов"""
        game = EducationalGame("Лото", "Классическое лото", 3, 6)
        data = game.to_dict()
        assert data == {
            "name": "Лото",
            "description": "Классическое лото",
            "min_age": 3,
            "max_age": 6,
            "required_materials": []  # пустой список
        }
    
    def test_from_dict(self):
        """Тест десериализации из словаря"""
        data = {
            "name": "Пазлы",
            "description": "Складываем картинку",
            "min_age": 3,
            "max_age": 5
        }
        game = EducationalGame.from_dict(data)
        assert game.name == "Пазлы"
        assert game.description == "Складываем картинку"
        assert game.min_age == 3
        assert game.max_age == 5
    
    def test_from_dict_invalid_age_range(self):
        """Тест десериализации с неверным возрастным диапазоном"""
        data = {
            "name": "Пазлы",
            "description": "Описание",
            "min_age": 5,
            "max_age": 3
        }
        with pytest.raises(ValueError):
            EducationalGame.from_dict(data)

class TestStateManager:
    """Тесты для класса StateManager"""
    
    @pytest.fixture
    def temp_dir(self):
        """Фикстура для временной директории"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def state_manager(self, temp_dir):
        """Фикстура StateManager с временным файлом"""
        filename = os.path.join(temp_dir, "test_state.json")
        return StateManager(filename)
    
    @pytest.fixture
    def sample_data(self):
        """Фикстура с тестовыми данными"""
        return {
            "children": [
                {"name": "Маша", "age": 4, "state": "hungry"},
                {"name": "Петя", "age": 5, "state": "awake"}
            ],
            "materials": [
                {"title": "Кубики", "quantity": 10}
            ]
        }
    
    def test_save_success(self, state_manager, sample_data):
        """Тест успешного сохранения"""
        # Сохраняем
        state_manager.save(sample_data)
        
        # Проверяем, что файл создан
        assert os.path.exists(state_manager.filename)
        
        # Проверяем содержимое
        with open(state_manager.filename, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        
        assert loaded == sample_data
    
    def test_save_creates_directory(self, temp_dir):
        """Тест создания директории при сохранении"""
        # Файл во вложенной директории
        filename = os.path.join(temp_dir, "subdir", "nested", "state.json")
        manager = StateManager(filename)
        
        manager.save({"test": "data"})
        
        # Проверяем, что директория создана
        assert os.path.exists(os.path.dirname(filename))
        assert os.path.exists(filename)
    
    def test_save_error_permission(self, state_manager, sample_data):
        """Тест ошибки сохранения (нет прав)"""
        # Делаем файл только для чтения
        with open(state_manager.filename, 'w') as f:
            f.write("test")
        os.chmod(state_manager.filename, 0o444)
        
        with pytest.raises(SaveError) as exc_info:
            state_manager.save(sample_data)
        assert "Ошибка сохранения" in str(exc_info.value)
    
    def test_load_success(self, state_manager, sample_data):
        """Тест успешной загрузки"""
        # Сначала сохраняем
        state_manager.save(sample_data)
        
        # Загружаем
        loaded = state_manager.load()
        assert loaded == sample_data
    
    def test_load_file_not_found(self, state_manager):
        """Тест загрузки несуществующего файла"""
        with pytest.raises(LoadError) as exc_info:
            state_manager.load()
        assert "не найден" in str(exc_info.value)
    
    def test_load_corrupted_json(self, state_manager):
        """Тест загрузки испорченного JSON"""
        # Создаем файл с некорректным JSON
        with open(state_manager.filename, 'w', encoding='utf-8') as f:
            f.write("{this is not json}")
        
        with pytest.raises(LoadError) as exc_info:
            state_manager.load()
        assert "испорчен" in str(exc_info.value)
    
    def test_load_or_default_existing(self, state_manager, sample_data):
        """Тест load_or_default с существующим файлом"""
        state_manager.save(sample_data)
        
        default = {"default": "data"}
        loaded = state_manager.load_or_default(default)
        
        assert loaded == sample_data
        assert loaded != default
    
    def test_load_or_default_missing(self, state_manager):
        """Тест load_or_default с отсутствующим файлом"""
        default = {"default": "data"}
        loaded = state_manager.load_or_default(default)
        
        assert loaded == default
    
    def test_load_or_default_corrupted(self, state_manager):
        """Тест load_or_default с испорченным файлом"""
        # Создаем испорченный файл
        with open(state_manager.filename, 'w', encoding='utf-8') as f:
            f.write("corrupted")
        
        default = {"default": "data"}
        loaded = state_manager.load_or_default(default)
        
        # Должен вернуть default при ошибке загрузки
        assert loaded == default
    
    def test_unicode_handling(self, state_manager):
        """Тест обработки Unicode"""
        data = {
            "name": "Детский сад №75",
            "children": ["Маша", "Петя", "Саша"]
        }
        
        state_manager.save(data)
        loaded = state_manager.load()
        
        assert loaded == data

class TestKindergarten:
    """Интеграционные тесты для класса Kindergarten"""
    
    @pytest.fixture
    def temp_state_file(self):
        """Фикстура для временного файла состояния"""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            yield f.name
        # Очистка после теста
        if os.path.exists(f.name):
            os.unlink(f.name)
    
    @pytest.fixture
    def kindergarten(self, temp_state_file):
        """Фикстура детского сада с временным файлом"""
        kg = Kindergarten("Анна Петровна", state_file=temp_state_file)
        # Очищаем данные для тестов
        kg.children = []
        kg.parents = []
        kg.materials = []
        kg.games = []
        kg.groups = []
        kg._create_default_groups()
        return kg
    
    def test_initialization(self, kindergarten):
        """Тест инициализации детского сада"""
        assert kindergarten.teacher.name == "Анна Петровна"
        assert len(kindergarten.get_all_children()) == 0
        assert len(kindergarten.get_all_groups()) == 5  # 5 групп по умолчанию
    
    def test_add_child(self, kindergarten):
        """Тест добавления ребенка"""
        child = kindergarten.add_child("Маша", 4)
        assert child.name == "Маша"
        assert child.age == 4
        assert child in kindergarten.children
    
    def test_add_child_duplicate_name(self, kindergarten):
        """Тест добавления ребенка с существующим именем (допустимо)"""
        kindergarten.add_child("Маша", 4)
        child2 = kindergarten.add_child("Маша", 5)  # Можно с тем же именем
        assert len(kindergarten.children) == 2
    
    def test_get_child_by_name(self, kindergarten):
        """Тест поиска ребенка по имени"""
        kindergarten.add_child("Маша", 4)
        kindergarten.add_child("Петя", 5)
        
        child = kindergarten.get_child_by_name("Маша")
        assert child is not None
        assert child.name == "Маша"
        
        child = kindergarten.get_child_by_name("неизвестный")
        assert child is None
    
    def test_get_child_or_raise(self, kindergarten):
        """Тест получения ребенка с исключением"""
        kindergarten.add_child("Маша", 4)
        
        child = kindergarten.get_child_or_raise("Маша")
        assert child.name == "Маша"
        
        with pytest.raises(ChildNotFoundError):
            kindergarten.get_child_or_raise("неизвестный")
    
    def test_add_parent(self, kindergarten):
        """Тест добавления родителя"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        assert parent.name == "Ольга"
        assert parent.child == child
        assert parent in kindergarten.parents
    
    def test_add_parent_child_not_in_kindergarten(self, kindergarten):
        """Тест добавления родителя для ребенка не из сада"""
        child = Child("Маша", 4)  # не добавляем в сад
        
        with pytest.raises(ValueError) as exc_info:
            kindergarten.add_parent("Ольга", child)
        assert "не найден в саду" in str(exc_info.value)
    
    def test_get_parent_for_child(self, kindergarten):
        """Тест получения родителя для ребенка"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        found_parent = kindergarten.get_parent_for_child(child)
        assert found_parent == parent
        
        # Для ребенка без родителя
        child2 = kindergarten.add_child("Петя", 5)
        assert kindergarten.get_parent_for_child(child2) is None
    
    def test_get_parent_or_raise(self, kindergarten):
        """Тест получения родителя с исключением"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        found_parent = kindergarten.get_parent_or_raise(child)
        assert found_parent == parent
        
        child2 = kindergarten.add_child("Петя", 5)
        with pytest.raises(ParentNotFoundError):
            kindergarten.get_parent_or_raise(child2)
    
    def test_add_material(self, kindergarten):
        """Тест добавления материала"""
        material = kindergarten.add_material("Кубики", 10)
        assert material.title == "Кубики"
        assert material.quantity == 10
        assert material in kindergarten.materials
    
    def test_add_game(self, kindergarten):
        """Тест добавления игры"""
        game = kindergarten.add_game("Лото", "Описание", 3, 6)
        assert game.name == "Лото"
        assert game in kindergarten.games
    
    def test_get_games_for_child(self, kindergarten):
        """Тест получения игр для ребенка"""
        kindergarten.add_game("Лото", "Описание", 3, 6)
        kindergarten.add_game("Мозаика", "Описание", 4, 7)
        kindergarten.add_game("Пазлы", "Описание", 1, 2)
        
        child = kindergarten.add_child("Маша", 4)
        games = kindergarten.get_games_for_child(child)
        
        assert len(games) == 2  # Лото и Мозаика
        assert all(game.can_play(4) for game in games)
    
    def test_feed_child(self, kindergarten):
        """Тест кормления ребенка"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        # Приводим ребенка
        parent.drop_off()
        assert child.state == "hungry"
        
        # Кормим
        result = kindergarten.feed_child("Маша")
        assert result["success"] is True
        assert child.state == "awake"
    
    def test_feed_child_not_found(self, kindergarten):
        """Тест кормления несуществующего ребенка"""
        with pytest.raises(ChildNotFoundError):
            kindergarten.feed_child("Неизвестный")
    
    def test_put_to_sleep(self, kindergarten):
        """Тест укладывания спать"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        parent.drop_off()
        kindergarten.feed_child("Маша")  # теперь awake
        
        result = kindergarten.put_to_sleep("Маша")
        assert result["success"] is True
        assert child.state == "sleeping"
    
    def test_wake_up(self, kindergarten):
        """Тест пробуждения"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        
        parent.drop_off()
        kindergarten.feed_child("Маша")
        kindergarten.put_to_sleep("Маша")
        assert child.state == "sleeping"
        
        result = kindergarten.wake_up("Маша")
        assert result["success"] is True
        assert child.state == "awake"
    
    def test_start_game(self, kindergarten):
        """Тест начала игры"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        kindergarten.add_game("Лото", "Описание", 3, 6)
        
        parent.drop_off()
        kindergarten.feed_child("Маша")  # теперь awake
        
        result = kindergarten.start_game("Маша", "Лото")
        assert result["success"] is True
        assert child.state == "playing"
    
    def test_start_game_wrong_age(self, kindergarten):
        """Тест начала игры с неподходящим возрастом"""
        child = kindergarten.add_child("Маша", 2)
        parent = kindergarten.add_parent("Ольга", child)
        kindergarten.add_game("Лото", "Описание", 3, 6)
        
        parent.drop_off()
        kindergarten.feed_child("Маша")
        
        with pytest.raises(GameAgeError):
            kindergarten.start_game("Маша", "Лото")
    
    def test_finish_game(self, kindergarten):
        """Тест завершения игры"""
        child = kindergarten.add_child("Маша", 4)
        parent = kindergarten.add_parent("Ольга", child)
        kindergarten.add_game("Лото", "Описание", 3, 6)
        
        parent.drop_off()
        kindergarten.feed_child("Маша")
        kindergarten.start_game("Маша", "Лото")
        assert child.state == "playing"
        
        result = kindergarten.finish_game("Маша")
        assert result["success"] is True
        assert child.state == "hungry"
    
    def test_drop_off_child(self, kindergarten):
        """Тест приведения ребенка"""
        child = kindergarten.add_child("Маша", 4)
        kindergarten.add_parent("Ольга", child)
        assert child.state == "left"
        
        result = kindergarten.drop_off_child("Маша")
        assert result["success"] is True
        assert child.state == "hungry"
    
    def test_pickup_child(self, kindergarten):
        """Тест забирания ребенка"""
        child = kindergarten.add_child("Маша", 4)
        kindergarten.add_parent("Ольга", child)
        
        kindergarten.drop_off_child("Маша")
        assert child.state != "left"
        
        result = kindergarten.pickup_child("Маша")
        assert result["success"] is True
        assert child.state == "left"
    
    def test_assign_child_to_group(self, kindergarten):
        """Тест определения ребенка в группу"""
        child = kindergarten.add_child("Маша", 4)
        
        result = kindergarten.assign_child_to_group("Маша", "средняя")
        assert "определен в группу" in result
        
        group = kindergarten.get_group_for_child(child)
        assert group is not None
        assert group.name == "средняя"
    
    def test_assign_child_to_wrong_group(self, kindergarten):
        """Тест определения ребенка в неподходящую группу"""
        child = kindergarten.add_child("Маша", 1)
        
        with pytest.raises(GroupError) as exc_info:
            kindergarten.assign_child_to_group("Маша", "старшая")
        assert "не подходит в группу" in str(exc_info.value)
    
    def test_assign_child_to_nonexistent_group(self, kindergarten):
        """Тест определения ребенка в несуществующую группу"""
        kindergarten.add_child("Маша", 4)
        
        with pytest.raises(GroupError) as exc_info:
            kindergarten.assign_child_to_group("Маша", "несуществующая")
        assert "не найдена" in str(exc_info.value)
    
    def test_move_child_between_groups(self, kindergarten):
        """Тест перемещения ребенка между группами"""
        child = kindergarten.add_child("Маша", 4)
        
        kindergarten.assign_child_to_group("Маша", "младшая")
        group1 = kindergarten.get_group_for_child(child)
        assert group1.name == "младшая"
        
        kindergarten.assign_child_to_group("Маша", "средняя")
        group2 = kindergarten.get_group_for_child(child)
        assert group2.name == "средняя"
        
        # Проверяем, что ребенка нет в первой группе
        assert child not in group1.get_children()
    
    def test_show_groups(self, kindergarten):
        """Тест отображения групп"""
        child = kindergarten.add_child("Маша", 4)
        kindergarten.assign_child_to_group("Маша", "средняя")
        
        result = kindergarten.show_groups()
        assert "ГРУППЫ ДЕТСКОГО САДА" in result
        assert "средняя" in result
        assert "Маша" in result
    
    def test_save_and_load_state(self, kindergarten, temp_state_file):
        """Тест сохранения и загрузки состояния"""
        # Добавляем данные
        child = kindergarten.add_child("Маша", 4)
        kindergarten.add_parent("Ольга", child)
        kindergarten.add_material("Кубики", 10)
        kindergarten.add_game("Лото", "Описание", 3, 6)
        kindergarten.assign_child_to_group("Маша", "средняя")
        
        # Сохраняем
        kindergarten.save_state()
        
        # Создаем новый экземпляр с тем же файлом
        kindergarten2 = Kindergarten("Анна Петровна", state_file=temp_state_file)
        
        # Проверяем, что данные загрузились
        assert len(kindergarten2.children) == 1
        assert kindergarten2.children[0].name == "Маша"
        assert len(kindergarten2.parents) == 1
        assert kindergarten2.parents[0].name == "Ольга"
        assert len(kindergarten2.materials) == 1
        assert kindergarten2.materials[0].title == "Кубики"
        assert len(kindergarten2.games) == 1
        assert kindergarten2.games[0].name == "Лото"
        
        # Проверяем группу
        group = kindergarten2.get_group_for_child(kindergarten2.children[0])
        assert group is not None
        assert group.name == "средняя"

# ============================================================================
# ЗАПУСК ТЕСТОВ
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src", "--cov-report=html"])