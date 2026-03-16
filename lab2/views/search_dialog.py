import tkinter as tk
from tkinter import ttk, messagebox

class SearchDialog:
    """Диалог для поиска студентов"""
    
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Поиск студентов")
        self.dialog.geometry("1000x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Параметры пагинации
        self.page_size = 10
        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0
        self.current_results = []
        
        # Переменные для ФИО студента (можно заполнять все)
        self.student_lastname = tk.StringVar()
        self.student_firstname = tk.StringVar()
        self.student_patronymic = tk.StringVar()
        
        # Для родителя
        self.parent_type = tk.StringVar(value="father")
        self.parent_lastname = tk.StringVar()
        self.parent_firstname = tk.StringVar()
        self.parent_patronymic = tk.StringVar()
        
        # Для братьев/сестер
        self.sibling_type = tk.StringVar(value="brothers")
        self.sibling_count = tk.StringVar()
        
        # Для зарплаты
        self.salary_parent = tk.StringVar(value="father")
        self.salary_min = tk.StringVar()
        self.salary_max = tk.StringVar()
        
        self.create_widgets()
        self.center_dialog()
        
        # Валидация только для чисел
        self.sibling_count.trace('w', lambda *args: self.validate_number(self.sibling_count))
        self.salary_min.trace('w', lambda *args: self.validate_income(self.salary_min))
        self.salary_max.trace('w', lambda *args: self.validate_income(self.salary_max))
    
    def center_dialog(self):
        """Центрирование окна"""
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
    
    def validate_number(self, var):
        """Только цифры для целых чисел"""
        value = var.get()
        if value and not value.isdigit():
            var.set(''.join(c for c in value if c.isdigit()))
    
    def validate_income(self, var):
        """Цифры и точка для зарплаты"""
        value = var.get()
        if value and not value.replace('.', '').isdigit():
            var.set(''.join(c for c in value if c.isdigit() or c == '.'))
    
    def create_widgets(self):
        """Создание интерфейса"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель с условиями
        left_frame = ttk.LabelFrame(main_frame, text="Условия поиска", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.create_search_criteria(left_frame)
        
        # Правая панель с результатами
        right_frame = ttk.LabelFrame(main_frame, text="Результаты поиска", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.create_results_area(right_frame)
    
    def create_search_criteria(self, parent):
        """Создание полей для условий поиска"""
        row = 0
        
        # ===== ФИО СТУДЕНТА =====
        ttk.Label(parent, text="ФИО студента:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        ttk.Label(parent, text="Фамилия:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.student_lastname, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(parent, text="Имя:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.student_firstname, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(parent, text="Отчество:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.student_patronymic, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Separator(parent, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        row += 1
        
        # ===== ФИО РОДИТЕЛЯ =====
        ttk.Label(parent, text="ФИО родителя:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # Выбор родителя
        radio_frame = ttk.Frame(parent)
        radio_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(radio_frame, text="Отец", variable=self.parent_type, 
                       value="father").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(radio_frame, text="Мать", variable=self.parent_type, 
                       value="mother").pack(side=tk.LEFT, padx=5)
        row += 1
        
        ttk.Label(parent, text="Фамилия:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.parent_lastname, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(parent, text="Имя:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.parent_firstname, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Label(parent, text="Отчество:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.parent_patronymic, width=20).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Separator(parent, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        row += 1
        
        # ===== БРАТЬЯ/СЕСТРЫ =====
        ttk.Label(parent, text="Братья и сестры:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        sibling_frame = ttk.Frame(parent)
        sibling_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(sibling_frame, text="Братья", variable=self.sibling_type,
                       value="brothers").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sibling_frame, text="Сестры", variable=self.sibling_type,
                       value="sisters").pack(side=tk.LEFT, padx=5)
        row += 1
        
        ttk.Label(parent, text="Количество:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=self.sibling_count, width=10).grid(
            row=row, column=1, sticky=tk.W, padx=5, pady=2)
        row += 1
        
        ttk.Separator(parent, orient='horizontal').grid(
            row=row, column=0, columnspan=2, sticky=tk.EW, pady=10)
        row += 1
        
        # ===== ЗАРПЛАТА =====
        ttk.Label(parent, text="Зарплата родителя:", font=('Arial', 10, 'bold')).grid(
            row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        row += 1
        
        salary_parent_frame = ttk.Frame(parent)
        salary_parent_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Radiobutton(salary_parent_frame, text="Отец", variable=self.salary_parent,
                       value="father").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(salary_parent_frame, text="Мать", variable=self.salary_parent,
                       value="mother").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Диапазон
        range_frame = ttk.Frame(parent)
        range_frame.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
        ttk.Label(range_frame, text="от").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.salary_min, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="до").pack(side=tk.LEFT)
        ttk.Entry(range_frame, textvariable=self.salary_max, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(range_frame, text="руб.").pack(side=tk.LEFT)
        row += 1
        
        # Кнопка поиска
        ttk.Button(parent, text="🔍 Найти", command=self.search, 
                  width=20).grid(row=row, column=0, columnspan=2, pady=20)
    
    def create_results_area(self, parent):
        """Таблица результатов"""
        columns = ('student_name', 'father_name', 'father_income', 
                  'mother_name', 'mother_income', 'brothers', 'sisters')
        
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set,
            height=15
        )
        
        # Заголовки
        self.results_table.heading('student_name', text='ФИО студента')
        self.results_table.heading('father_name', text='ФИО отца')
        self.results_table.heading('father_income', text='Зарплата отца')
        self.results_table.heading('mother_name', text='ФИО матери')
        self.results_table.heading('mother_income', text='Зарплата матери')
        self.results_table.heading('brothers', text='Братья')
        self.results_table.heading('sisters', text='Сестры')
        
        # Ширина колонок
        self.results_table.column('student_name', width=150)
        self.results_table.column('father_name', width=120)
        self.results_table.column('father_income', width=90)
        self.results_table.column('mother_name', width=120)
        self.results_table.column('mother_income', width=90)
        self.results_table.column('brothers', width=60)
        self.results_table.column('sisters', width=60)
        
        self.results_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_table.yview)
        
        # Пагинация
        self.create_pagination(parent)
    
    def create_pagination(self, parent):
        """Пагинация для результатов"""
        pagination_frame = ttk.Frame(parent)
        pagination_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(pagination_frame, text="Показывать по:").pack(side=tk.LEFT)
        self.page_size_var = tk.StringVar(value="10")
        page_size_combo = ttk.Combobox(
            pagination_frame,
            textvariable=self.page_size_var,
            values=[5, 10, 25, 50],
            width=5,
            state="readonly"
        )
        page_size_combo.pack(side=tk.LEFT, padx=5)
        page_size_combo.bind('<<ComboboxSelected>>', self.on_page_size_change)
        
        ttk.Button(pagination_frame, text="◀◀", command=self.go_first_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="◀", command=self.go_prev_page).pack(side=tk.LEFT, padx=2)
        
        self.page_info_label = ttk.Label(pagination_frame, text="Страница 1 из 1")
        self.page_info_label.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(pagination_frame, text="▶", command=self.go_next_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination_frame, text="▶▶", command=self.go_last_page).pack(side=tk.LEFT, padx=2)
        
        self.records_info_label = ttk.Label(pagination_frame, text="Найдено: 0")
        self.records_info_label.pack(side=tk.RIGHT, padx=10)
    
    def search(self):
        """Поиск"""
        criteria = self.collect_criteria()
        print(f"Критерии поиска: {criteria}")  # для отладки
        self.controller.search_students(criteria, self)
        
    def collect_criteria(self):
        """Собирает критерии поиска из полей ввода"""
        criteria = {}
        
        # ===== ФИО студента =====
        # Проверяем, заполнено ли несколько полей
        filled_fields = []
        if self.student_lastname.get():
            filled_fields.append(('surname', self.student_lastname.get().strip()))
        if self.student_firstname.get():
            filled_fields.append(('name', self.student_firstname.get().strip()))
        if self.student_patronymic.get():
            filled_fields.append(('patronymic', self.student_patronymic.get().strip()))
        
        if len(filled_fields) == 1:
            # Заполнено только одно поле - передаем тип
            criteria['student_name'] = {
                'type': filled_fields[0][0],
                'value': filled_fields[0][1]
            }
        elif len(filled_fields) > 1:
            # Заполнено несколько полей - склеиваем в строку
            full_name = ' '.join([value for _, value in filled_fields])
            criteria['student_name'] = full_name
        
        # ===== ФИО родителя =====
        parent_filled = []
        if self.parent_lastname.get():
            parent_filled.append(('surname', self.parent_lastname.get().strip()))
        if self.parent_firstname.get():
            parent_filled.append(('name', self.parent_firstname.get().strip()))
        if self.parent_patronymic.get():
            parent_filled.append(('patronymic', self.parent_patronymic.get().strip()))
        
        if parent_filled:
            parent_key = 'father_name' if self.parent_type.get() == "father" else 'mother_name'
            
            if len(parent_filled) == 1:
                # Одно поле
                criteria[parent_key] = {
                    'type': parent_filled[0][0],
                    'value': parent_filled[0][1]
                }
            else:
                # Несколько полей
                full_parent_name = ' '.join([value for _, value in parent_filled])
                criteria[parent_key] = full_parent_name
        
        # ===== Братья/сестры (без изменений) =====
        if self.sibling_count.get():
            try:
                count = int(self.sibling_count.get())
                if self.sibling_type.get() == "brothers":
                    criteria['brothers'] = count
                else:
                    criteria['sisters'] = count
            except ValueError:
                pass
        
        # ===== Зарплата (без изменений) =====
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

    def display_results(self, students, total_records):
        """Отображение результатов"""
        self.current_results = students
        self.total_records = total_records
        self.total_pages = (total_records + self.page_size - 1) // self.page_size
        if self.total_pages == 0:
            self.total_pages = 1
        
        # Очистка таблицы
        for item in self.results_table.get_children():
            self.results_table.delete(item)
        
        # Заполнение
        for student in students:
            self.results_table.insert('', tk.END, values=(
                student.student_name,
                student.father_name,
                f"{student.father_income:.2f}",
                student.mother_name,
                f"{student.mother_income:.2f}",
                student.brothers,
                student.sisters
            ))
        
        self.update_pagination_info()
    
    def update_pagination_info(self):
        """Обновление информации о страницах"""
        self.page_info_label.config(
            text=f"Страница {self.current_page} из {self.total_pages}"
        )
        self.records_info_label.config(
            text=f"Найдено: {self.total_records}"
        )
    
    def on_page_size_change(self, event=None):
        """Изменение количества на странице"""
        new_size = int(self.page_size_var.get())
        self.page_size = new_size
        self.current_page = 1
        self.search()
    
    def go_first_page(self):
        if self.current_page > 1:
            self.current_page = 1
            self.search()
    
    def go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.search()
    
    def go_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.search()
    
    def go_last_page(self):
        if self.current_page < self.total_pages:
            self.current_page = self.total_pages
            self.search()