import tkinter as tk
from tkinter import ttk, messagebox

class DeleteDialog:
    """Диалог для удаления студентов по условиям"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Удаление студентов")
        self.dialog.geometry("600x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Переменные для условий
        self.student_lastname = tk.StringVar()
        self.student_firstname = tk.StringVar()
        self.student_patronymic = tk.StringVar()
        
        self.parent_type = tk.StringVar(value="father")
        self.parent_lastname = tk.StringVar()
        self.parent_firstname = tk.StringVar()
        self.parent_patronymic = tk.StringVar()
        
        self.sibling_type = tk.StringVar(value="brothers")
        self.sibling_count = tk.StringVar()
        
        self.salary_parent = tk.StringVar(value="father")
        self.salary_min = tk.StringVar()
        self.salary_max = tk.StringVar()
        
        self.create_widgets()
        self.center_dialog()
        self.setup_validation()
    
    def center_dialog(self):
        """Центрирует диалог"""
        self.dialog.update_idletasks()
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_validation(self):
        """Валидация числовых полей"""
        self.sibling_count.trace('w', lambda *args: self.validate_number(self.sibling_count))
        self.salary_min.trace('w', lambda *args: self.validate_income(self.salary_min))
        self.salary_max.trace('w', lambda *args: self.validate_income(self.salary_max))
    
    def validate_number(self, var):
        """Только цифры"""
        value = var.get()
        if value and not value.isdigit():
            var.set(''.join(c for c in value if c.isdigit()))
    
    def validate_income(self, var):
        """Число с точкой"""
        value = var.get()
        if value and not value.replace('.', '').replace('-', '').isdigit():
            var.set(''.join(c for c in value if c.isdigit() or c == '.'))
    
    def create_widgets(self):
        """Создает интерфейс диалога"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        ttk.Label(main_frame, text="Условия удаления:", 
                 font=('Arial', 14, 'bold')).pack(pady=(0, 20))
        
        # ===== ФИО студента =====
        student_frame = ttk.LabelFrame(main_frame, text="ФИО студента", padding="10")
        student_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(student_frame, text="Фамилия:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(student_frame, textvariable=self.student_lastname, width=30).grid(row=0, column=1, pady=2, padx=5)
        
        ttk.Label(student_frame, text="Имя:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(student_frame, textvariable=self.student_firstname, width=30).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(student_frame, text="Отчество:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(student_frame, textvariable=self.student_patronymic, width=30).grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(student_frame, text="(можно заполнить одно или несколько полей)", 
                 foreground='gray', font=('Arial', 8)).grid(row=3, column=0, columnspan=2, pady=2)
        
        # ===== ФИО родителя =====
        parent_frame = ttk.LabelFrame(main_frame, text="ФИО родителя", padding="10")
        parent_frame.pack(fill=tk.X, pady=5)
        
        # Выбор родителя
        radio_frame = ttk.Frame(parent_frame)
        radio_frame.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Radiobutton(radio_frame, text="Отец", variable=self.parent_type, 
                       value="father").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Мать", variable=self.parent_type, 
                       value="mother").pack(side=tk.LEFT, padx=5)
        
        ttk.Label(parent_frame, text="Фамилия:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent_frame, textvariable=self.parent_lastname, width=30).grid(row=1, column=1, pady=2, padx=5)
        
        ttk.Label(parent_frame, text="Имя:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent_frame, textvariable=self.parent_firstname, width=30).grid(row=2, column=1, pady=2, padx=5)
        
        ttk.Label(parent_frame, text="Отчество:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent_frame, textvariable=self.parent_patronymic, width=30).grid(row=3, column=1, pady=2, padx=5)
        
        ttk.Label(parent_frame, text="(можно заполнить одно или несколько полей)", 
                 foreground='gray', font=('Arial', 8)).grid(row=4, column=0, columnspan=2, pady=2)
        
        # ===== Братья/сестры =====
        sibling_frame = ttk.LabelFrame(main_frame, text="Братья и сестры", padding="10")
        sibling_frame.pack(fill=tk.X, pady=5)
        
        # Выбор братья или сестры
        sibling_radio = ttk.Frame(sibling_frame)
        sibling_radio.pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(sibling_radio, text="Братья", variable=self.sibling_type,
                       value="brothers").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sibling_radio, text="Сестры", variable=self.sibling_type,
                       value="sisters").pack(side=tk.LEFT, padx=5)
        
        # Количество
        count_frame = ttk.Frame(sibling_frame)
        count_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(count_frame, text="Количество:").pack(side=tk.LEFT)
        ttk.Entry(count_frame, textvariable=self.sibling_count, width=10).pack(side=tk.LEFT, padx=5)
        
        # ===== Зарплата =====
        salary_frame = ttk.LabelFrame(main_frame, text="Зарплата родителя", padding="10")
        salary_frame.pack(fill=tk.X, pady=5)
        
        # Выбор родителя
        salary_radio = ttk.Frame(salary_frame)
        salary_radio.pack(anchor=tk.W, pady=5)
        ttk.Radiobutton(salary_radio, text="Отец", variable=self.salary_parent,
                       value="father").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(salary_radio, text="Мать", variable=self.salary_parent,
                       value="mother").pack(side=tk.LEFT, padx=5)
        
        # Диапазон
        range_frame = ttk.Frame(salary_frame)
        range_frame.pack(anchor=tk.W, pady=5)
        ttk.Label(range_frame, text="от").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.salary_min, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="до").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.salary_max, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="руб.").pack(side=tk.LEFT)
        
        # ===== Кнопки =====
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=30)
        
        ttk.Button(button_frame, text="Удалить", command=self.delete,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy,
                  width=15).pack(side=tk.LEFT, padx=5)
    
    def collect_criteria(self):
        """Собирает условия удаления"""
        criteria = {}
        
        # ФИО студента (объединяем все заполненные поля)
        student_parts = []
        if self.student_lastname.get():
            student_parts.append(self.student_lastname.get().strip())
        if self.student_firstname.get():
            student_parts.append(self.student_firstname.get().strip())
        if self.student_patronymic.get():
            student_parts.append(self.student_patronymic.get().strip())
        
        if student_parts:
            criteria['student_name'] = ' '.join(student_parts)
        
        # ФИО родителя
        parent_parts = []
        if self.parent_lastname.get():
            parent_parts.append(self.parent_lastname.get().strip())
        if self.parent_firstname.get():
            parent_parts.append(self.parent_firstname.get().strip())
        if self.parent_patronymic.get():
            parent_parts.append(self.parent_patronymic.get().strip())
        
        if parent_parts:
            parent_key = 'father_name' if self.parent_type.get() == "father" else 'mother_name'
            criteria[parent_key] = ' '.join(parent_parts)
        
        # Братья/сестры
        if self.sibling_count.get():
            try:
                count = int(self.sibling_count.get())
                if self.sibling_type.get() == "brothers":
                    criteria['brothers'] = count
                else:
                    criteria['sisters'] = count
            except ValueError:
                pass
        
        # Зарплата
        salary_parent = self.salary_parent.get()
        if self.salary_min.get():
            try:
                min_salary = float(self.salary_min.get())
                if salary_parent == "father":
                    criteria['father_income_min'] = min_salary
                else:
                    criteria['mother_income_min'] = min_salary
            except ValueError:
                pass
        
        if self.salary_max.get():
            try:
                max_salary = float(self.salary_max.get())
                if salary_parent == "father":
                    criteria['father_income_max'] = max_salary
                else:
                    criteria['mother_income_max'] = max_salary
            except ValueError:
                pass
        
        return criteria
    
    def delete(self):
        """Удаляет записи по условиям"""
        criteria = self.collect_criteria()
        if not criteria:
            messagebox.showwarning("Предупреждение", "Заполните хотя бы одно условие!")
            return
        
        try:
            # Сначала ищем записи, которые будут удалены
            students = self.controller.db.search_students(criteria, limit=1000, offset=0)
            
            if not students:
                messagebox.showinfo("Информация", "Записей, соответствующих условию, не найдено")
                return
            
            # Формируем сообщение со списком найденных
            message = f"Найдено записей: {len(students)}\n\n"
            message += "Будут удалены:\n"
            
            # Показываем первых 10, чтобы не перегружать сообщение
            for i, student in enumerate(students[:10], 1):
                message += f"{i}. {student.student_name}\n"
            
            if len(students) > 10:
                message += f"... и еще {len(students) - 10}\n"
            
            message += f"\nВсего будет удалено: {len(students)} записей"
            
            # Спрашиваем подтверждение
            if messagebox.askyesno("Подтверждение удаления", message, icon='warning'):
                # Выполняем удаление
                self.controller.confirm_delete(criteria, self.dialog)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске записей: {str(e)}")