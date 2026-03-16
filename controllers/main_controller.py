import tkinter as tk
from tkinter import messagebox
from models.database import Database
from models.student import Student
from views.main_window import MainWindow
from views.add_dialog import AddDialog
from views.search_dialog import SearchDialog
from views.delete_dialog import DeleteDialog


class MainController:
    """Главный контроллер приложения"""
    
    def __init__(self, root):
        self.root = root
        
        # Инициализируем модель (базу данных)
        try:
            self.db = Database("data/students.db")
        except Exception as e:
            messagebox.showerror("Ошибка БД", f"Не удалось подключиться к базе данных: {str(e)}")
            raise e
        
        # Создаем представление (главное окно)
        self.view = MainWindow(root, self)
        
        # Загружаем первую страницу данных
        self.load_first_page()
    
    def load_first_page(self):
        """Загружает первую страницу данных"""
        try:
            # Получаем общее количество записей
            total = self.db.get_total_count()
            
            # Загружаем первую страницу
            students = self.db.get_students_page(limit=self.view.page_size, offset=0)
            
            # Обновляем отображение
            self.view.display_students(students)
            self.view.update_pagination(total, 1)  # 1 - первая страница
            
        except Exception as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {str(e)}")
    
    def load_page(self, page_num):
        """Загружает указанную страницу"""
        try:
            offset = (page_num - 1) * self.view.page_size
            students = self.db.get_students_page(
                limit=self.view.page_size, 
                offset=offset
            )
            self.view.display_students(students)
            self.view.update_pagination(self.db.get_total_count(), page_num)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить страницу: {str(e)}")
    
    def change_page_size(self, new_size):
        """Изменяет количество записей на странице"""
        self.view.page_size = new_size
        self.load_first_page(1)  # Перезагружаем с новым размером
    
    def add_student(self, student_data):
        """Добавляет нового студента"""
        try:
            student = Student(
                student_name=student_data['student_name'],
                father_name=student_data['father_name'],
                father_income=student_data['father_income'],
                mother_name=student_data['mother_name'],
                mother_income=student_data['mother_income'],
                brothers=student_data['brothers'],
                sisters=student_data['sisters']
            )
            
            self.db.add_student(student)
            messagebox.showinfo("Успех", "Студент успешно добавлен!")
            
            # Перезагружаем первую страницу
            self.load_first_page()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить студента: {str(e)}")
    
    def open_add_dialog(self):
        """Открывает диалог добавления студента"""
        AddDialog(self.root, self)
    
    def search_students(self, criteria, search_dialog):
        """Поиск студентов по критериям"""
        try:
            # Вычисляем offset для пагинации
            offset = (search_dialog.current_page - 1) * search_dialog.page_size
            
            # Выполняем поиск
            students = self.db.search_students(
                criteria, 
                limit=search_dialog.page_size, 
                offset=offset
            )
            
            # Получаем общее количество найденных записей
            total = self.db.search_count(criteria)
            
            # Отображаем результаты
            search_dialog.display_results(students, total)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}")
    
    def open_search_dialog(self):
        """Открывает диалог поиска"""
        SearchDialog(self.root, self)
    
    # ===== НОВЫЕ МЕТОДЫ ДЛЯ УДАЛЕНИЯ =====
    
    def open_delete_dialog(self):
        """Открывает диалог удаления"""
        try:
            DeleteDialog(self.view.root, self)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть диалог удаления: {str(e)}")
    
    def delete_students(self, criteria, dialog):
        """Поиск записей для удаления (вызывается из диалога)"""
        try:
            # Просто ищем записи, не удаляем
            students = self.db.search_students(criteria, limit=1000, offset=0)
            return students
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {str(e)}")
            return []

    def confirm_delete(self, criteria, dialog):
        """Подтвержденное удаление"""
        try:
            count = self.db.delete_students(criteria)
            
            if count > 0:
                messagebox.showinfo("Успех", f"Записи успешно удалены!\nУдалено: {count}")
                # Обновляем главное окно
                self.load_first_page()
            else:
                messagebox.showinfo("Информация", "Записей для удаления не найдено")
            
            dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")   
    
    def save_to_xml(self, filepath):
        """Сохраняет данные в XML файл"""
        try:
            from utils.xml_handler import XMLExport
            
            # Получаем всех студентов из БД
            students = self.db.get_all_students()
            
            if not students:
                messagebox.showwarning("Предупреждение", "Нет данных для сохранения!")
                return
            
            # Сохраняем в XML
            XMLExport.save_to_file(students, filepath)
            
            messagebox.showinfo("Успех", f"Данные сохранены в файл:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def load_from_xml(self, filepath):
        """Загружает данные из XML файла"""
        try:
            from utils.xml_handler import XMLImport
            
            # Загружаем студентов из XML
            students = XMLImport.load_from_file(filepath)
            
            if not students:
                messagebox.showwarning("Предупреждение", "В файле нет студентов!")
                return
            
            # Спрашиваем подтверждение
            msg = f"Найдено студентов: {len(students)}\n"
            msg += "Добавить их в базу данных?"
            
            if messagebox.askyesno("Подтверждение", msg):
                # Добавляем в БД
                added = 0
                for student in students:
                    self.db.add_student(student)
                    added += 1
                
                messagebox.showinfo("Успех", f"Добавлено студентов: {added}")
                
                # Перезагружаем отображение
                self.load_first_page()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
                
 