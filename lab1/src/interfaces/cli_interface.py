from src.core.kindergarten import Kindergarten
from src.models.child import Child
from src.utils.exceptions import (
    KindergartenException, ChildNotFoundError,
    ParentNotFoundError, GameNotFoundError, GroupError,
    MaterialNotFoundError, InvalidStateError,
    GameAgeError, SaveError, LoadError, InvalidAgeError 
)

class CLIInterface:
    
    def __init__(self, kindergarten: Kindergarten):
        self.kindergarten = kindergarten
    
    def run(self) -> None:
        while True:
            self._show_menu() 
            choice = input("\nВыберите действие: ").strip() 
           
            try:
                if choice == "1":
                    self._show_children()
                elif choice == "2":
                    self._add_child()
                elif choice == "3":
                    self._feed_child()
                elif choice == "4":
                    self._put_to_sleep()
                elif choice == "5":
                    self._wake_up()
                elif choice == "6":
                    self._play_game()
                elif choice == "7":
                    self._finish_game()
                elif choice == "8":
                    self._parent_action()
                elif choice == "9":
                    self._show_resources()
                elif choice == "10":
                    self._add_resources()
                elif choice == "11":
                    self._show_groups()
                elif choice == "12":
                    self._assign_to_group()
                elif choice == "13":
                    self._organize_educational_process()  # НОВАЯ КОМАНДА
                elif choice == "14":
                    self._show_educational_report()  
                elif choice == "15":
                    self._save_and_exit()
                    break
                elif choice == "0":
                    self._exit_without_save()
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")
                
            except ChildNotFoundError as e:
                print(f" Ошибка: {e}")
            except InvalidAgeError as e:
                print(f"Ошибка: {e}")
            except ParentNotFoundError as e:
                print(f" Ошибка: {e}")
            except GameNotFoundError as e:
                print(f" Ошибка: {e}")
            except MaterialNotFoundError as e:
                print(f" Ошибка: {e}")
            except InvalidStateError as e:
                print(f" Ошибка: {e}")
            except GameAgeError as e:
                print(f" Ошибка: {e}")
            except SaveError as e:
                print(f" Ошибка сохранения: {e}")
            except LoadError as e:
                print(f" Ошибка загрузки: {e}")
            except KindergartenException as e:
                print(f" Ошибка детского сада: {e}")
            except Exception as e:
                print(f" Неожиданная ошибка: {e}")
            input("\nНажмите Enter чтобы продолжить...")
    
    def _show_menu(self) -> None:
        print("\n" + "="*60)
        print("ДЕТСКИЙ САД - ГЛАВНОЕ МЕНЮ")
        print("="*60)
        print(f"Воспитатель: {self.kindergarten.teacher.name}")
        print(f"Детей: {len(self.kindergarten.get_all_children())}")
        print("-"*60)
        print("1.  Показать всех детей")
        print("2.  Добавить ребенка")
        print("3.  Покормить ребенка")
        print("4.  Уложить спать")
        print("5.  Разбудить")
        print("6.  Поиграть")
        print("7.  Закончить игру")
        print("8.  Привести/забрать ребенка")
        print("9.  Показать материалы и игры")
        print("10. Добавить материалы/игры")
        print("11. Показать группы")           
        print("12. Определить ребенка в группу")
        print("13. Организовать учебный процесс")  
        print("14. Показать отчет об учебном процессе") 
        print("15. Сохранить и выйти")
        print("0.  Выйти без сохранения")
        print("-"*60)
    
    def _show_children(self) -> None:
        children = self.kindergarten.get_all_children()
        
        if not children:
            print("\nВ детском саду нет детей")
            return
        
        print("\nДЕТИ В ДЕТСКОМ САДУ:")
        print("-"*40)
        for i, child in enumerate(children, 1):
            print(f"{i}. {child}")
    
    def _add_child(self) -> None:
        """Добавить ребенка с выбором группы"""
        print("\nДОБАВЛЕНИЕ РЕБЕНКА")
        print("-"*40)
    
        name = input("Имя ребенка: ").strip()
        if not name:
            print("Имя не может быть пустым")
            return
    
        try:
            age = int(input("Возраст: ").strip())
        except ValueError:
            print("Возраст должен быть числом")
            return
    
        # Показываем доступные группы
        groups = self.kindergarten.get_all_groups()
        if not groups:
            print("Ошибка: нет доступных групп")
            return
    
        print("\nДоступные группы:")
        for i, group in enumerate(groups, 1):
            age_ok = group.min_age <= age <= group.max_age
            mark = "✓" if age_ok else "✗"
            print(f"{i}. {mark} {group}")
    
        print("\n✓ - подходит по возрасту, ✗ - не подходит")
    
        try:
            choice = int(input("\nВыберите группу (номер): ")) - 1
            if 0 <= choice < len(groups):
                selected_group = groups[choice]
            else:
                print("Неверный номер")
                return
        except ValueError:
            print("Введите число")
            return
    
    # Создаем ребенка
        try:
            child = self.kindergarten.add_child(name, age)
        # Определяем в выбранную группу
            try:
                result = self.kindergarten.assign_child_to_group(child.name, selected_group.name)
                print(result)
            except Exception as e:
                print(f"Ошибка при определении в группу: {e}")
                self._ask_for_parent(child)
                return 
        # Спрашиваем про родителя
            self._ask_for_parent(child)
        
        except InvalidAgeError as e:
            print(f"Ошибка: {e}")

    def _ask_for_parent(self, child: Child) -> None:
        add_parent = input("\nДобавить родителя? (д/н): ").strip().lower()
        if add_parent in ["д", "да", "y", "yes"]:
            parent_name = input("Имя родителя: ").strip()
            if parent_name:
                try:
                    self.kindergarten.add_parent(parent_name, child)
                    print(f"Добавлен родитель: {parent_name}")
                except ValueError as e:
                    print(f"Ошибка: {e}")
    
    def _feed_child(self) -> None:
        name = input("Имя ребенка: ").strip()
        result = self.kindergarten.feed_child(name)
        print(result["message"])
    
    def _put_to_sleep(self) -> None:
        name = input("Имя ребенка: ").strip()
        result = self.kindergarten.put_to_sleep(name)
        print(result["message"])
    
    def _wake_up(self) -> None:
        name = input("Имя ребенка: ").strip()
        result = self.kindergarten.wake_up(name)
        print(result["message"])
    
    def _play_game(self) -> None:
        child_name = input("Имя ребенка: ").strip()
        child = self.kindergarten.get_child_or_raise(child_name)        
        games = self.kindergarten.get_games_for_child(child)
        
        if not games:
            print(f"Для {child.name} нет подходящих игр")
            return
        
        print(f"\nИГРЫ ДЛЯ {child.name}:")
        for i, game in enumerate(games, 1):
            print(f"{i}. {game}")
        
        try:
            choice = int(input("\nВыберите игру: ")) - 1
            if 0 <= choice < len(games):
                game = games[choice]
                result = self.kindergarten.start_game(child_name, game.name)
                print(result["message"])
            else:
                print("Неверный номер")
        except ValueError:
            print("Введите число")
    
    def _finish_game(self) -> None:
        name = input("Имя ребенка: ").strip()
        result = self.kindergarten.finish_game(name)
        print(result["message"])
    
    def _parent_action(self) -> None: 
        name = input("Имя ребенка: ").strip()
        child = self.kindergarten.get_child_or_raise(name)
        parent = self.kindergarten.get_parent_or_raise(child)
        action = input("Что сделать? (привести/забрать): ").strip().lower()
        if action in ["привести", "п"]:
           result = self.kindergarten.drop_off_child(name)
        elif action in ["забрать", "з"]:
            result = self.kindergarten.pickup_child(name)
        else:
            print("Непонятная команда")
            return
        print(result["message"])
    
    def _show_resources(self) -> None:
        materials = self.kindergarten.get_all_materials()
        games = self.kindergarten.get_all_games()
        
        print("\nУЧЕБНЫЕ МАТЕРИАЛЫ:")
        if materials:
            for material in materials:
                print(f"   {material}")
        else:
            print("   Нет материалов")
        
        print("\nРАЗВИВАЮЩИЕ ИГРЫ:")
        if games:
            for game in games:
                print(f"   {game}")
        else:
            print("   Нет игр")
    
    def _add_resources(self) -> None:
        print("\nЧТО ДОБАВИТЬ?")
        print("1. Учебный материал")
        print("2. Развивающую игру")
        
        choice = input("Выберите: ").strip()
        
        if choice == "1":
            title = input("Название материала: ").strip()
            try:
                quantity = int(input("Количество: ").strip())
                self.kindergarten.add_material(title, quantity)
                print(f"Материал '{title}' добавлен")
            except ValueError:
                print("Количество должно быть числом")
        
        elif choice == "2":
            name = input("Название игры: ").strip()
            description = input("Описание: ").strip()
            try:
                min_age = int(input("Минимальный возраст: ").strip())
                max_age = int(input("Максимальный возраст: ").strip())
                self.kindergarten.add_game(name, description, min_age, max_age)
                print(f"Игра '{name}' добавлена")
            except ValueError:
                print("Возраст должен быть числом")
        
        else:
            print("Неверный выбор")
    
    def _show_groups(self) -> None:
        print(self.kindergarten.show_groups())

    def _assign_to_group(self) -> None:
        child_name = input("Имя ребенка: ").strip()
    
        # Показываем доступные группы
        print("\nДоступные группы:")
        groups = self.kindergarten.get_all_groups()
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group}")
    
        try:
            choice = int(input("\nВыберите группу: ")) - 1
            if 0 <= choice < len(groups):
                group = groups[choice]
                result = self.kindergarten.assign_child_to_group(child_name, group.name)
                print(result)
            else:
                print("Неверный номер")
        except ValueError:
            print("Введите число")
        except GroupError as e:
            print(f"Ошибка: {e}")

    def _save_and_exit(self) -> None:
        self.kindergarten.save_state()
        print("\nДо свидания! Состояние сохранено.")
    
    def _exit_without_save(self) -> None:
        print("\nДо свидания! Состояние НЕ сохранено.")

    def _organize_educational_process(self) -> None:
        """Организация учебного процесса"""
        print("\nОРГАНИЗАЦИЯ УЧЕБНОГО ПРОЦЕССА")
        print("-"*40)
    
    # Показываем доступные игры
        games = self.kindergarten.get_all_games()
        if not games:
            print("Нет доступных игр/занятий")
            return
    
        print("\nДоступные занятия:")
        for i, game in enumerate(games, 1):
            print(f"{i}. {game}")
    
        try:
            game_choice = int(input("\nВыберите занятие (номер): ")) - 1
            if game_choice < 0 or game_choice >= len(games):
                print("Неверный номер")
                return
            game = games[game_choice]
        except ValueError:
            print("Введите число")
            return
    
    # Спрашиваем про группу
        group_choice = input("\nПровести для конкретной группы? (д/н): ").strip().lower()
        group_name = None
    
        if group_choice in ["д", "да", "y", "yes"]:
            print("\nДоступные группы:")
            groups = self.kindergarten.get_all_groups()
            for i, group in enumerate(groups, 1):
                print(f"{i}. {group}")
        
            try:
                group_idx = int(input("Выберите группу: ")) - 1
                if 0 <= group_idx < len(groups):
                    group_name = groups[group_idx].name
                else:
                    print("Неверный номер")
                    return
            except ValueError:
                print("Введите число")
                return
    
    # Организуем учебный процесс
        result = self.kindergarten.organize_educational_process(game.name, group_name)
        print(f"\n{result}")

    def _show_educational_report(self) -> None:
        """Показать отчет об учебном процессе"""
        print(self.kindergarten.get_educational_report())