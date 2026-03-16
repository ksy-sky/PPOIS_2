#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Лабораторная работа №2
Вариант 10: Учет студентов и их семей
"""

import tkinter as tk
from tkinter import messagebox
from controllers.main_controller import MainController

def main():
    """Точка входа в приложение"""
    try:
        # Создаем корневое окно
        root = tk.Tk()
        root.title("Система учета студентов - Вариант 10")
        root.geometry("1200x700")
        
        # Устанавливаем иконку (если есть)
        try:
            root.iconbitmap("icon.ico")
        except:
            pass  # игнорируем, если нет иконки
        
        # Создаем контроллер (он создаст все остальное)
        app = MainController(root)
        
        # Запускаем главный цикл
        root.mainloop()
        
    except Exception as e:
        # Если что-то пошло не так при запуске
        messagebox.showerror("Ошибка запуска", f"Не удалось запустить приложение: {str(e)}")
        raise e

if __name__ == "__main__":
    main()