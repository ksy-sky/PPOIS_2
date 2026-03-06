# Лабораторная работа №1  
**Модель детского сада**

## Важные сущности

- воспитатель
- дети
- учебные материалы
- родители
- развивающие игры
- группы
- детский сад

## Описание проекта

Консольная программа-симулятор детского сада.  
Пользователь может:
- добавлять детей и родителей
- кормить, укладывать спать, будить детей
- играть в развивающие игры
- приводить и забирать детей из сада
- добавлять учебные материалы и игры
- распределять детей по возрастным группам
- проводить учебные занятия с расходом материалов
- просматривать отчеты о состоянии сада
- сохранять и загружать состояние между запусками (JSON-файл)

## Основные классы

### `models.Child` (ребенок)
**Атрибуты**
- `name: str` — имя ребенка
- `age: int` — возраст (от 1 до 7)
- `_state: str` — текущее состояние

**Состояния** (константы класса)
- `hungry` — голоден
- `awake` — бодрствует
- `playing` — играет
- `sleeping` — спит
- `left` — дома (не в саду)

**Методы**
- `update_state(new_state: str) -> None` — изменить состояние
- `make_hungry() -> bool` — сделать голодным (из awake/playing)
- `state` (property) — получить текущее состояние
- `to_dict() -> dict` — сериализация
- `from_dict(data: dict) -> Child` — десериализация

### `models.Teacher` (воспитатель)
**Атрибуты**
- `name: str` — имя воспитателя

**Методы**
- `feed_child(child: Child) -> dict` — покормить ребенка
- `put_to_sleep(child: Child) -> dict` — уложить спать
- `wake_up(child: Child) -> dict` — разбудить
- `start_game(child: Child, game_name: str) -> dict` — начать игру
- `finish_game(child: Child) -> dict` — закончить игру
- `conduct_lesson(children: List[Child], game: EducationalGame, materials: dict) -> dict` — провести занятие (расходует материалы)

### `models.Parent` (родитель)
**Атрибуты**
- `name: str` — имя родителя
- `child: Child` — ребенок

**Методы**
- `drop_off() -> dict` — привести ребенка в сад
- `pickup() -> dict` — забрать ребенка домой
- `to_dict() -> dict` — сериализация

### `models.Group` (группа)
**Атрибуты**
- `name: str` — название группы
- `min_age: int` — минимальный возраст
- `max_age: int` — максимальный возраст
- `children: List[Child]` — дети в группе
- `capacity: int` — вместимость (по умолчанию 15)

**Типы групп** (константы класса)
- `ясли` (1-2 года)
- `младшая` (3-4 года)
- `средняя` (4-5 лет)
- `старшая` (5-6 лет)
- `подготовительная` (6-7 лет)

**Методы**
- `add_child(child: Child) -> None` — добавить ребенка (с проверкой возраста и вместимости)
- `remove_child(child: Child) -> None` — удалить ребенка
- `get_children() -> List[Child]` — получить список детей
- `get_count() -> int` — количество детей
- `has_place() -> bool` — есть ли место
- `to_dict() -> dict` — сериализация

### `models.TeachingMaterial` (учебный материал)
**Атрибуты**
- `title: str` — название
- `quantity: int` — количество

**Методы**
- `use(amount: int = 1) -> None` — использовать материал (уменьшает количество)
- `to_dict() -> dict` — сериализация

### `models.EducationalGame` (развивающая игра)
**Атрибуты**
- `name: str` — название
- `description: str` — описание
- `min_age: int` — минимальный возраст
- `max_age: int` — максимальный возраст
- `required_materials: List[str]` — необходимые материалы

**Методы**
- `can_play(child_age: int) -> bool` — можно ли играть ребенку этого возраста
- `check_age(child_name: str, child_age: int) -> None` — проверить возраст (бросает `GameAgeError`)
- `check_materials(available_materials: dict) -> List[str]` — проверить наличие материалов
- `to_dict() -> dict` — сериализация

### `core.Kindergarten` (детский сад)
**Атрибуты**
- `teacher: Teacher` — воспитатель
- `children: List[Child]` — все дети
- `parents: List[Parent]` — все родители
- `materials: List[TeachingMaterial]` — все материалы
- `games: List[EducationalGame]` — все игры
- `groups: List[Group]` — все группы
- `state_manager: StateManager` — менеджер сохранения

**Методы управления**
- `add_child(name: str, age: int) -> Child` — добавить ребенка
- `add_parent(name: str, child: Child) -> Parent` — добавить родителя
- `add_material(title: str, quantity: int) -> TeachingMaterial` — добавить материал
- `add_game(name: str, description: str, min_age: int, max_age: int, required_materials: List[str] = []) -> EducationalGame` — добавить игру

**Методы операций**
- `feed_child(child_name: str) -> dict` — покормить
- `put_to_sleep(child_name: str) -> dict` — уложить
- `wake_up(child_name: str) -> dict` — разбудить
- `start_game(child_name: str, game_name: str) -> dict` — начать игру
- `finish_game(child_name: str) -> dict` — закончить игру
- `drop_off_child(child_name: str) -> dict` — привести
- `pickup_child(child_name: str) -> dict` — забрать
- `assign_child_to_group(child_name: str, group_name: str) -> str` — определить в группу
- `organize_educational_process(game_name: str, group_name: Optional[str] = None) -> str` — провести занятие

**Методы получения данных**
- `get_child_by_name(name: str) -> Optional[Child]` — найти ребенка
- `get_parent_for_child(child: Child) -> Optional[Parent]` — найти родителя
- `get_games_for_child(child: Child) -> List[EducationalGame]` — игры для ребенка
- `get_all_groups() -> List[Group]` — все группы
- `get_group_for_child(child: Child) -> Optional[Group]` — группа ребенка
- `get_educational_report() -> str` — отчет об учебном процессе

**Методы сохранения**
- `save_state() -> None` — сохранить состояние в JSON
- `_load_state() -> None` — загрузить состояние

### `core.StateManager` (менеджер состояния)
**Атрибуты**
- `filename: str` — путь к файлу сохранения

**Методы**
- `save(data: dict) -> None` — сохранить данные в JSON
- `load() -> dict` — загрузить данные из JSON
- `load_or_default(default: dict) -> dict` — загрузить или вернуть default

### Исключения (все наследуются от `KindergartenException`)

| Исключение | Описание |
|------------|----------|
| `ChildNotFoundError` | Ребенок не найден |
| `InvalidAgeError` | Недопустимый возраст (меньше 1 или больше 7) |
| `ParentNotFoundError` | У ребенка нет родителя |
| `GameNotFoundError` | Игра не найдена |
| `MaterialNotFoundError` | Материал не найден |
| `InvalidStateError` | Недопустимое действие для текущего состояния |
| `GameAgeError` | Игра не подходит по возрасту |
| `GroupError` | Ошибка, связанная с группами |
| `SaveError` | Ошибка сохранения |
| `LoadError` | Ошибка загрузки |
