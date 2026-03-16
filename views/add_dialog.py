import tkinter as tk
from tkinter import ttk, messagebox

class AddDialog:
    """Диалог для добавления нового студента"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Добавление нового студента")
        self.dialog.geometry("600x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)  # делаем диалог модальным
        self.dialog.grab_set()  # захватываем фокус
        
        # Переменные для хранения введенных данных
        self.student_name = tk.StringVar()
        self.father_name = tk.StringVar()
        self.father_income = tk.StringVar()
        self.mother_name = tk.StringVar()
        self.mother_income = tk.StringVar()
        self.brothers = tk.StringVar(value="0")
        self.sisters = tk.StringVar(value="0")
        
        self.create_widgets()
        
        # Центрируем диалог относительно родительского окна
        self.center_dialog()
    
    def center_dialog(self):
        """Центрирует диалог относительно родительского окна"""
        self.dialog.update_idletasks()
        
        # Получаем размеры родительского окна
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # Получаем размеры диалога
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Вычисляем позицию для центрирования
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Создает элементы интерфейса диалога"""
        
        # Основной фрейм с отступами
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title_label = ttk.Label(
            main_frame, 
            text="Введите данные студента:", 
            font=('Arial', 12, 'bold')
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky=tk.W)
        
        # Поля ввода
        row = 1
        
        # ФИО студента
        ttk.Label(main_frame, text="ФИО студента:*").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.student_name, width=40).grid(
            row=row, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10
        )
        row += 1
        
        # Данные отца
        ttk.Label(main_frame, text="ДАННЫЕ ОТЦА", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        ttk.Label(main_frame, text="ФИО отца:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.father_name, width=40).grid(
            row=row, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        ttk.Label(main_frame, text="Заработок отца:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        income_frame = ttk.Frame(main_frame)
        income_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Entry(income_frame, textvariable=self.father_income, width=15).pack(side=tk.LEFT)
        ttk.Label(income_frame, text="руб.").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10
        )
        row += 1
        
        # Данные матери
        ttk.Label(main_frame, text="ДАННЫЕ МАТЕРИ", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        ttk.Label(main_frame, text="ФИО матери:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        ttk.Entry(main_frame, textvariable=self.mother_name, width=40).grid(
            row=row, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        row += 1
        
        ttk.Label(main_frame, text="Заработок матери:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        income_frame = ttk.Frame(main_frame)
        income_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Entry(income_frame, textvariable=self.mother_income, width=15).pack(side=tk.LEFT)
        ttk.Label(income_frame, text="руб.").pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Разделитель
        ttk.Separator(main_frame, orient='horizontal').grid(
            row=row, column=0, columnspan=3, sticky=tk.EW, pady=10
        )
        row += 1
        
        # Братья и сестры
        ttk.Label(main_frame, text="БРАТЬЯ И СЕСТРЫ", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )
        row += 1
        
        siblings_frame = ttk.Frame(main_frame)
        siblings_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        ttk.Label(siblings_frame, text="Число братьев:").pack(side=tk.LEFT)
        ttk.Entry(siblings_frame, textvariable=self.brothers, width=5).pack(side=tk.LEFT, padx=(5, 15))
        
        ttk.Label(siblings_frame, text="Число сестер:").pack(side=tk.LEFT)
        ttk.Entry(siblings_frame, textvariable=self.sisters, width=5).pack(side=tk.LEFT, padx=(5, 0))
        row += 1
        
        # Подсказка об обязательных полях
        ttk.Label(
            main_frame, 
            text="* - обязательное поле", 
            foreground='gray'
        ).grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(20, 0))
        
        # Кнопки
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row+1, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="Сохранить", 
            command=self.save_student,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Отмена", 
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Привязываем обработчики для валидации ввода
        self.father_income.trace('w', lambda *args: self.validate_income(self.father_income))
        self.mother_income.trace('w', lambda *args: self.validate_income(self.mother_income))
        self.brothers.trace('w', lambda *args: self.validate_number(self.brothers))
        self.sisters.trace('w', lambda *args: self.validate_number(self.sisters))
    
    def validate_income(self, var):
        """Валидация поля заработка (только числа и точка)"""
        value = var.get()
        if value and not value.replace('.', '').replace('-', '').isdigit():
            var.set(''.join(c for c in value if c.isdigit() or c == '.'))
    
    def validate_number(self, var):
        """Валидация числового поля (только целые числа)"""
        value = var.get()
        if value and not value.isdigit():
            var.set(''.join(c for c in value if c.isdigit()))
    
    def save_student(self):
        """Сохраняет данные студента"""
        # Проверяем обязательные поля
        if not self.student_name.get().strip():
            messagebox.showerror("Ошибка", "ФИО студента обязательно для заполнения!")
            return
        
        # Собираем данные
        try:
            student_data = {
                'student_name': self.student_name.get().strip(),
                'father_name': self.father_name.get().strip(),
                'father_income': float(self.father_income.get() or 0),
                'mother_name': self.mother_name.get().strip(),
                'mother_income': float(self.mother_income.get() or 0),
                'brothers': int(self.brothers.get() or 0),
                'sisters': int(self.sisters.get() or 0)
            }
            
            # Вызываем контроллер для сохранения
            self.controller.add_student(student_data)
            
            # Закрываем диалог
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверный формат данных: {str(e)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")