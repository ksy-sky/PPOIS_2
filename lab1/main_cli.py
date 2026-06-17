
from src.core.kindergarten import Kindergarten
from src.interfaces.cli_interface import CLIInterface


def create_sample_data(kindergarten):
    """
    Создание примерных данных для демонстрации работы программы
    """
    print("\n" + "="*60)
    print(" СОЗДАНИЕ ПРИМЕРНЫХ ДАННЫХ")
    print("="*60)
    
    # ===== ДЕТИ =====
    print("\nДобавляем детей...")
    masha = kindergarten.add_child("Маша", 4)
    petya = kindergarten.add_child("Петя", 5)
    dasha = kindergarten.add_child("Даша", 3)
    kolya = kindergarten.add_child("Коля", 2)
    sonya = kindergarten.add_child("Соня", 6)
    
    # ===== РОДИТЕЛИ =====
    print("\nДобавляем родителей...")
    kindergarten.add_parent("Ольга", masha)
    kindergarten.add_parent("Иван", petya)
    kindergarten.add_parent("Елена", dasha)
    kindergarten.add_parent("Сергей", kolya)
    kindergarten.add_parent("Марина", sonya)
    
    # ===== УЧЕБНЫЕ МАТЕРИАЛЫ =====
    print("\nДобавляем учебные материалы...")
    kindergarten.add_material("Краски", 10)
    kindergarten.add_material("Пластилин", 8)
    kindergarten.add_material("Цветная бумага", 20)
    kindergarten.add_material("Клей", 5)
    kindergarten.add_material("Карандаши", 15)
    kindergarten.add_material("Кисточки", 7)
    
    # ===== ИГРЫ (развлечение) =====
    print("\n Добавляем развивающие игры...")
    kindergarten.add_game(
        "Лото", 
        "Классическое лото с картинками", 
        3, 6, 
        [],  # без материалов
        False  # это игра
    )
    kindergarten.add_game(
        "Мозаика", 
        "Собираем узоры из кусочков", 
        4, 7, 
        [],  # без материалов
        False  # это игра
    )
    kindergarten.add_game(
        "Пазлы", 
        "Складываем картинку", 
        3, 5, 
        [],  # без материалов
        False  # это игра
    )
    kindergarten.add_game(
        "Домино", 
        "Игра с картинками", 
        3, 6, 
        [],  # без материалов
        False  # это игра
    )
    
    # ===== УЧЕБНЫЕ ЗАНЯТИЯ =====
    print("\nДобавляем учебные занятия...")
    kindergarten.add_game(
        "Рисование", 
        "Учимся рисовать красками", 
        3, 6, 
        ["Краски", "Кисточки", "Цветная бумага"],  # требуются материалы
        True  # это учебное занятие
    )
    kindergarten.add_game(
        "Лепка", 
        "Лепим фигурки из пластилина", 
        3, 6, 
        ["Пластилин"],  # требуются материалы
        True  # это учебное занятие
    )
    kindergarten.add_game(
        "Аппликация", 
        "Делаем поделки из бумаги", 
        4, 7, 
        ["Цветная бумага", "Клей"],  # требуются материалы
        True  # это учебное занятие
    )
    kindergarten.add_game(
        "Конструирование", 
        "Строим из кубиков", 
        2, 5, 
        ["Кубики"],  # требуются материалы
        True  # это учебное занятие
    )
    
    # ===== РАСПРЕДЕЛЕНИЕ ПО ГРУППАМ =====
    print("\nРаспределяем детей по группам...")
    try:
        kindergarten.assign_child_to_group("Маша", "средняя")
        kindergarten.assign_child_to_group("Петя", "старшая")
        kindergarten.assign_child_to_group("Даша", "младшая")
        kindergarten.assign_child_to_group("Коля", "ясли")
        kindergarten.assign_child_to_group("Соня", "подготовительная")
        print("  ✓ Дети распределены по группам")
    except Exception as e:
        print(f" Ошибка при распределении: {e}")
    
    print("\n" + "="*60)
    print("Примерные данные успешно созданы!")
    print("="*60)
    print("\nДоступные команды:")
    print(" 6 - Поиграть (Лото, Мозаика, Пазлы, Домино)")
    print(" 13 - Учебные занятия (Рисование, Лепка, Аппликация, Конструирование)")
    print(" 14 - Отчет об учебном процессе")
    print()


def main():
    """
    Главная функция запуска программы
    """
    print("="*60)
    print(" ЛАБОРАТОРНАЯ РАБОТА №1: МОДЕЛЬ ДЕТСКОГО САДА №75")
    print("="*60)
    print("\nЗагрузка сохраненного состояния...")
    
    # Создаем детский сад (автоматически загружает сохранение)
    kindergarten = Kindergarten("Анна Петровна")
    
    # Если детей нет (первый запуск), создаем примерные данные
    if not kindergarten.get_all_children():
        create_sample_data(kindergarten)
        # Сразу сохраняем созданные данные
        kindergarten.save_state()
        print("\nПримерные данные сохранены для следующих запусков.")
    else:
        print(f"\nЗагружено {len(kindergarten.get_all_children())} детей из сохранения.")
        
        # Показываем краткую информацию о загруженных данных
        games_count = len(kindergarten.get_all_games())
        materials_count = len(kindergarten.get_all_materials())
        print(f" Игр: {games_count}")
        print(f" Материалов: {materials_count}")
    
    # Создаем и запускаем CLI интерфейс
    cli = CLIInterface(kindergarten)
    
    print("\nЗапуск интерфейса...")
    cli.run()


if __name__ == "__main__":
    main()
