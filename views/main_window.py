import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class MainWindow:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # Настройки пагинации
        self.page_size = 10
        self.current_page = 1
        self.total_pages = 1
        self.total_records = 0
        
        # Режим отображения
        self.view_mode = tk.StringVar(value="table")
        
        # Создаем интерфейс
        self.create_menu()
        self.create_toolbar()
        self.create_main_area()
        self.create_status_bar()
        self.create_pagination_controls()
        
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить в XML", command=self.save_to_xml)
        file_menu.add_command(label="Загрузить из XML", command=self.load_from_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Записи
        records_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Записи", menu=records_menu)
        records_menu.add_command(label="Добавить", command=self.open_add_dialog)
        records_menu.add_command(label="Поиск", command=self.open_search_dialog)
        records_menu.add_command(label="Удалить", command=self.open_delete_dialog)
        
        # Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_radiobutton(label="Таблица", variable=self.view_mode,
                                 value="table", command=self.switch_view)
        view_menu.add_radiobutton(label="Дерево", variable=self.view_mode,
                                 value="tree", command=self.switch_view)
    
    def create_toolbar(self):
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=2, pady=2)
        
        ttk.Button(toolbar, text="💾 Сохранить", 
                  command=self.save_to_xml).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="📂 Загрузить", 
                  command=self.load_from_xml).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(toolbar, text="➕ Добавить", 
                  command=self.open_add_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🔍 Поиск", 
                  command=self.open_search_dialog).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="✖ Удалить", 
                  command=self.open_delete_dialog).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        ttk.Button(toolbar, text="📊 Таблица", 
                  command=lambda: self.switch_view_mode("table")).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="🌳 Дерево", 
                  command=lambda: self.switch_view_mode("tree")).pack(side=tk.LEFT, padx=2)
    
    def create_main_area(self):
        """Создает основную область с таблицей и деревом"""
        # Контейнер для таблицы
        self.table_frame = ttk.Frame(self.root)
        self.create_table_view()
        
        # Контейнер для дерева
        self.tree_frame = ttk.Frame(self.root)
        self.create_tree_view()
        
        # Показываем таблицу по умолчанию
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree_frame.pack_forget()
    
    def create_table_view(self):
        """Создает табличное представление"""
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Таблица
        columns = ('student_name', 'father_name', 'father_income', 
                  'mother_name', 'mother_income', 'brothers', 'sisters')
        
        self.table = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show='headings',
            yscrollcommand=scrollbar.set
        )
        
        # Заголовки
        self.table.heading('student_name', text='ФИО студента')
        self.table.heading('father_name', text='ФИО отца')
        self.table.heading('father_income', text='Зарплата отца')
        self.table.heading('mother_name', text='ФИО матери')
        self.table.heading('mother_income', text='Зарплата матери')
        self.table.heading('brothers', text='Братья')
        self.table.heading('sisters', text='Сестры')
        
        # Ширина колонок
        self.table.column('student_name', width=200)
        self.table.column('father_name', width=180)
        self.table.column('father_income', width=100)
        self.table.column('mother_name', width=180)
        self.table.column('mother_income', width=100)
        self.table.column('brothers', width=60)
        self.table.column('sisters', width=60)
        
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.table.yview)
    
    def create_tree_view(self):
        """Создает древовидное представление"""
        # Скроллбар
        scrollbar = ttk.Scrollbar(self.tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Дерево
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=('value',),
            show='tree headings',
            yscrollcommand=scrollbar.set
        )
        
        # Заголовки
        self.tree.heading('#0', text='Студент / Поле')
        self.tree.heading('value', text='Значение')
        self.tree.column('#0', width=300)
        self.tree.column('value', width=250)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)
    
    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_bar, text="Готов к работе",
                                     relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def create_pagination_controls(self):
        pagination = ttk.Frame(self.root)
        pagination.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        
        # Количество записей
        ttk.Label(pagination, text="Показывать по:").pack(side=tk.LEFT)
        self.page_size_var = tk.StringVar(value="10")
        page_combo = ttk.Combobox(pagination, textvariable=self.page_size_var,
                                  values=[5, 10, 25, 50, 100], width=5, state="readonly")
        page_combo.pack(side=tk.LEFT, padx=5)
        page_combo.bind('<<ComboboxSelected>>', self.on_page_size_change)
        
        # Кнопки
        ttk.Button(pagination, text="◀◀", command=self.go_first_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination, text="◀", command=self.go_prev_page).pack(side=tk.LEFT, padx=2)
        
        self.page_info = ttk.Label(pagination, text="Страница 1 из 1")
        self.page_info.pack(side=tk.LEFT, padx=10)
        
        ttk.Button(pagination, text="▶", command=self.go_next_page).pack(side=tk.LEFT, padx=2)
        ttk.Button(pagination, text="▶▶", command=self.go_last_page).pack(side=tk.LEFT, padx=2)
        
        self.records_info = ttk.Label(pagination, text="Всего записей: 0")
        self.records_info.pack(side=tk.RIGHT, padx=10)
    
    def display_students(self, students):
        """Отображает студентов в текущем режиме"""
        if self.view_mode.get() == "table":
            self.display_table(students)
        else:
            self.display_tree(students)
    
    def display_table(self, students):
        """Отображает в таблице"""
        # Очищаем
        for item in self.table.get_children():
            self.table.delete(item)
        
        # Заполняем
        for student in students:
            self.table.insert('', tk.END, values=(
                student.student_name,
                student.father_name,
                f"{student.father_income:.2f}",
                student.mother_name,
                f"{student.mother_income:.2f}",
                student.brothers,
                student.sisters
            ))
    
    def display_tree(self, students):
        """Отображает в виде дерева"""
        # Очищаем
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Заполняем
        for student in students:
            # Корень - студент
            student_id = self.tree.insert('', tk.END,
                                         text=student.student_name,
                                         open=False,
                                         values=('',))
            
            # Отец
            self.tree.insert(student_id, tk.END,
                            text="Отец",
                            values=(f"{student.father_name} ({student.father_income:.2f} руб.)",))
            
            # Мать
            self.tree.insert(student_id, tk.END,
                            text="Мать",
                            values=(f"{student.mother_name} ({student.mother_income:.2f} руб.)",))
            
            # Братья
            self.tree.insert(student_id, tk.END,
                            text="Братья",
                            values=(str(student.brothers),))
            
            # Сестры
            self.tree.insert(student_id, tk.END,
                            text="Сестры",
                            values=(str(student.sisters),))
    
    def update_pagination(self, total_records, current_page):
        """Обновляет информацию о пагинации"""
        self.total_records = total_records
        self.current_page = current_page
        self.total_pages = (total_records + self.page_size - 1) // self.page_size
        
        if self.total_pages == 0:
            self.total_pages = 1
        
        self.page_info.config(text=f"Страница {self.current_page} из {self.total_pages}")
        self.records_info.config(text=f"Всего записей: {self.total_records}")
        self.status_label.config(text=f"Показано записей: {min(self.page_size, self.total_records)}")
    
    # Методы пагинации
    def go_first_page(self):
        if self.total_records > 0:
            self.current_page = 1
            self.controller.load_page(self.current_page)
            self.update_pagination(self.total_records, self.current_page)

    def go_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.controller.load_page(self.current_page)
            self.update_pagination(self.total_records, self.current_page)

    def go_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.controller.load_page(self.current_page)
            self.update_pagination(self.total_records, self.current_page)
    
    def go_last_page(self):
        if self.total_records > 0:
            self.current_page = self.total_pages
            self.controller.load_page(self.current_page)
            self.update_pagination(self.total_records, self.current_page)

    def on_page_size_change(self, event=None):
        try:
            new_size = int(self.page_size_var.get())
            self.page_size = new_size
            self.current_page = 1
            self.controller.change_page_size(new_size)
        except:
            pass
    
    def switch_view(self):
        """Переключает между таблицей и деревом"""
        if self.view_mode.get() == "table":
            self.table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.tree_frame.pack_forget()
        else:
            self.tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.table_frame.pack_forget()
        
        # Перезагружаем текущую страницу
        self.controller.load_page(self.current_page)
    
    def switch_view_mode(self, mode):
        self.view_mode.set(mode)
        self.switch_view()
    
    # Методы открытия диалогов
    def open_add_dialog(self):
        from views.add_dialog import AddDialog
        AddDialog(self.root, self.controller)
    
    def open_search_dialog(self):
        from views.search_dialog import SearchDialog
        SearchDialog(self.root, self.controller)
    
    def open_delete_dialog(self):
        from views.delete_dialog import DeleteDialog
        DeleteDialog(self.root, self.controller)
    
    # XML методы
    def save_to_xml(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            initialdir="./data"
        )
        if filepath:
            self.controller.save_to_xml(filepath)
    
    def load_from_xml(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")],
            initialdir="./data"
        )
        if filepath:
            self.controller.load_from_xml(filepath)