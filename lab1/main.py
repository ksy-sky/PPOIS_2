#!/usr/bin/env python3
from src.core.kindergarten import Kindergarten
from src.interfaces.cli_interface import CLIInterface

def create_sample_data(kindergarten):
    print("\n Создание примерных данных...")
    
    # Дети
    masha = kindergarten.add_child("Маша", 4)
    petya = kindergarten.add_child("Петя", 5)
    dasha = kindergarten.add_child("Даша", 3)
    
    # Родители
    kindergarten.add_parent("Ольга", masha)
    kindergarten.add_parent("Иван", petya)
    
    # Материалы
    kindergarten.add_material("Кубики", 10)
    kindergarten.add_material("Краски", 5)
    kindergarten.add_material("Пластилин", 3)
    
    # Игры
    kindergarten.add_game("Лото", "Классическое лото с картинками", 3, 6)
    kindergarten.add_game("Мозаика", "Собираем узоры из кусочков", 4, 7)
    kindergarten.add_game("Пазлы", "Складываем картинку", 3, 5)
    
    print(" Примерные данные созданы")


def main():
    """Главная функция"""
    print("="*60)
    print(" ЛАБОРАТОРНАЯ РАБОТА №1: МОДЕЛЬ ДЕТСКОГО САДА")
    print("="*60)
    
    # Создаем детский сад (автоматически загружает сохранение)
    kindergarten = Kindergarten("Анна Петровна")
    
    # Если детей нет, создаем примерные
    if not kindergarten.get_all_children():
        create_sample_data(kindergarten)
    
    # Создаем и запускаем CLI интерфейс
    cli = CLIInterface(kindergarten)
    cli.run()


if __name__ == "__main__":
    main()