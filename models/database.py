import sqlite3
from .student import Student

class Database:
    """Класс для работы с SQLite базой данных"""
    
    def __init__(self, db_path="data/students.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_table()
    
    def connect(self):
        """Устанавливает соединение с БД"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
    
    def disconnect(self):
        """Закрывает соединение с БД"""
        if self.connection:
            self.connection.close()
    
    def create_table(self):
        """Создает таблицу students, если её нет"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                father_name TEXT,
                father_income REAL DEFAULT 0,
                mother_name TEXT,
                mother_income REAL DEFAULT 0,
                brothers INTEGER DEFAULT 0,
                sisters INTEGER DEFAULT 0
            )
        ''')
        self.connection.commit()
    
    def add_student(self, student):
        """Добавляет нового студента в БД"""
        self.cursor.execute('''
            INSERT INTO students 
            (student_name, father_name, father_income, mother_name, mother_income, brothers, sisters)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', student.to_tuple())
        self.connection.commit()
        return self.cursor.lastrowid
    
    def get_all_students(self):
        """Возвращает всех студентов"""
        self.cursor.execute('SELECT * FROM students ORDER BY student_name')
        rows = self.cursor.fetchall()
        return [Student.from_tuple(tuple(row)[1:], row[0]) for row in rows]
    
    def get_students_page(self, limit=10, offset=0):
        """Возвращает страницу студентов для пагинации"""
        self.cursor.execute('''
            SELECT * FROM students 
            ORDER BY student_name 
            LIMIT ? OFFSET ?
        ''', (limit, offset))
        rows = self.cursor.fetchall()
        return [Student.from_tuple(tuple(row)[1:], row[0]) for row in rows]
    
    def get_total_count(self):
        """Возвращает общее количество записей"""
        self.cursor.execute('SELECT COUNT(*) FROM students')
        return self.cursor.fetchone()[0]
    
    def analyze_name_input(self, text):
        """
        Анализирует введенный текст и определяет тип поиска
        Возвращает: (тип_поиска, данные_для_поиска)
        """
        text = text.strip()
        if not text:
            return None, None
        
        words = text.split()
        
        # Одно слово
        if len(words) == 1:
            word = words[0]
            
            # Проверяем окончания для определения типа
            if word.endswith(('вич', 'вна')):
                return 'patronymic', word  # Отчество
            elif word.endswith(('ов', 'ев', 'ин', 'ын')):
                return 'surname', word  # Фамилия
            else:
                return 'name', word  # Имя
        
        # Два слова - фамилия + имя
        elif len(words) == 2:
            return 'first_last', {'surname': words[0], 'name': words[1]}
        
        # Три и более слова - полное ФИО
        else:
            return 'full', {
                'surname': words[0],
                'name': words[1],
                'patronymic': ' '.join(words[2:])
            }
       
    def build_name_condition(self, name_data, field_name):
        """
        Строит SQL условие для поиска по ФИО с учетом контекста
        """
        # Если это словарь с типом (новый формат)
        if isinstance(name_data, dict):
            search_type = name_data.get('type')
            value = name_data.get('value')
            
            if not value:
                return None, []
            
            # Экранируем спецсимволы для LIKE
            value = value.replace('_', '\\_').replace('%', '\\%')
            
            # Поиск по имени (одно слово)
            if search_type == 'name':
                return (
                    f"({field_name} LIKE ? ESCAPE '\\' OR {field_name} LIKE ? ESCAPE '\\' OR {field_name} LIKE ? ESCAPE '\\')",
                    [f'% {value} %', f'{value} %', f'% {value}']
                )
            
            # Поиск по фамилии (одно слово)
            elif search_type == 'surname':
                return (
                    f"({field_name} LIKE ? ESCAPE '\\' OR {field_name} LIKE ? ESCAPE '\\')",
                    [f'{value} %', f'% {value} %']
                )
            
            # Поиск по отчеству (одно слово)
            elif search_type == 'patronymic':
                return (
                    f"({field_name} LIKE ? ESCAPE '\\' OR {field_name} LIKE ? ESCAPE '\\')",
                    [f'% {value}', f'% {value} %']
                )
        
        # Если это строка - значит ввели несколько слов (полное ФИО или фамилия+имя)
        elif isinstance(name_data, str):
            return self._build_multi_word_condition(name_data, field_name)
        
        return None, []

    def _build_multi_word_condition(self, search_text, field_name):
        """
        Поиск по нескольким словам (полное ФИО или фамилия+имя)
        Ищем как последовательность слов в любом порядке
        """
        words = search_text.strip().split()
        if not words:
            return None, []
        
        conditions = []
        params = []
        
        # Для каждого слова создаем условие, что оно должно быть где-то в строке
        for word in words:
            word = word.replace('_', '\\_').replace('%', '\\%')
            conditions.append(f"{field_name} LIKE ? ESCAPE '\\'")
            params.append(f'%{word}%')
        
        # Все слова должны присутствовать
        return f"({' AND '.join(conditions)})", params

    def _build_name_condition_auto(self, search_text, field_name):
        """Старый автоматический анализ (на всякий случай)"""
        if not search_text:
            return None, []
        
        search_type, data = self.analyze_name_input(search_text)
        
        if search_type == 'name':
            return (
                f"({field_name} LIKE ? OR {field_name} LIKE ? OR {field_name} LIKE ?)",
                [f'% {data} %', f'{data} %', f'% {data}']
            )
        elif search_type == 'surname':
            return (
                f"({field_name} LIKE ? OR {field_name} LIKE ?)",
                [f'{data} %', f'% {data} %']
            )
        elif search_type == 'patronymic':
            return (
                f"({field_name} LIKE ? OR {field_name} LIKE ?)",
                [f'% {data}', f'% {data} %']
            )
        elif search_type == 'first_last':
            return (
                f"{field_name} LIKE ?",
                [f"{data['surname']} {data['name']}%"]
            )
        elif search_type == 'full':
            full_name = f"{data['surname']} {data['name']} {data['patronymic']}"
            return (
                f"({field_name} = ? OR {field_name} LIKE ?)",
                [full_name, f'{full_name} %']
            )
        
        return None, []

    def search_students(self, criteria, limit=10, offset=0):
        """
        Поиск студентов по критериям с умным анализом ФИО
        """
        query = 'SELECT * FROM students WHERE 1=1'
        params = []
        
        # Умный поиск по ФИО студента
        if criteria.get('student_name'):
            condition, cond_params = self.build_name_condition(
                criteria['student_name'], 'student_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        # Умный поиск по ФИО отца
        if criteria.get('father_name'):
            condition, cond_params = self.build_name_condition(
                criteria['father_name'], 'father_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        # Умный поиск по ФИО матери
        if criteria.get('mother_name'):
            condition, cond_params = self.build_name_condition(
                criteria['mother_name'], 'mother_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        # Поиск по числу братьев
        if criteria.get('brothers') is not None:
            query += " AND brothers = ?"
            params.append(criteria['brothers'])
        
        # Поиск по числу сестер
        if criteria.get('sisters') is not None:
            query += " AND sisters = ?"
            params.append(criteria['sisters'])
        
        # Поиск по зарплате отца (нижняя граница)
        if criteria.get('father_income_min') is not None:
            query += " AND father_income >= ?"
            params.append(criteria['father_income_min'])
        
        # Поиск по зарплате отца (верхняя граница)
        if criteria.get('father_income_max') is not None:
            query += " AND father_income <= ?"
            params.append(criteria['father_income_max'])
        
        # Поиск по зарплате матери (нижняя граница)
        if criteria.get('mother_income_min') is not None:
            query += " AND mother_income >= ?"
            params.append(criteria['mother_income_min'])
        
        # Поиск по зарплате матери (верхняя граница)
        if criteria.get('mother_income_max') is not None:
            query += " AND mother_income <= ?"
            params.append(criteria['mother_income_max'])
        
        # Добавляем сортировку и пагинацию
        query += " ORDER BY student_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        print(f"SQL Query: {query}")  # для отладки
        print(f"Params: {params}")     # для отладки
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        return [Student.from_tuple(tuple(row)[1:], row[0]) for row in rows]
    
    def search_count(self, criteria):
        """
        Возвращает количество записей, соответствующих критериям поиска
        """
        query = 'SELECT COUNT(*) FROM students WHERE 1=1'
        params = []
        
        # Те же условия, что и в search_students
        if criteria.get('student_name'):
            condition, cond_params = self.build_name_condition(
                criteria['student_name'], 'student_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        if criteria.get('father_name'):
            condition, cond_params = self.build_name_condition(
                criteria['father_name'], 'father_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        if criteria.get('mother_name'):
            condition, cond_params = self.build_name_condition(
                criteria['mother_name'], 'mother_name'
            )
            if condition:
                query += f" AND ({condition})"
                params.extend(cond_params)
        
        if criteria.get('brothers') is not None:
            query += " AND brothers = ?"
            params.append(criteria['brothers'])
        
        if criteria.get('sisters') is not None:
            query += " AND sisters = ?"
            params.append(criteria['sisters'])
        
        if criteria.get('father_income_min') is not None:
            query += " AND father_income >= ?"
            params.append(criteria['father_income_min'])
        
        if criteria.get('father_income_max') is not None:
            query += " AND father_income <= ?"
            params.append(criteria['father_income_max'])
        
        if criteria.get('mother_income_min') is not None:
            query += " AND mother_income >= ?"
            params.append(criteria['mother_income_min'])
        
        if criteria.get('mother_income_max') is not None:
            query += " AND mother_income <= ?"
            params.append(criteria['mother_income_max'])
        
        self.cursor.execute(query, params)
        return self.cursor.fetchone()[0]
    
    def delete_students(self, criteria):
        """
        Удаляет студентов по критериям
        Возвращает количество удаленных записей
        """
        # Сначала получаем количество записей для удаления
        count = self.search_count(criteria)
        
        if count > 0:
            query = 'DELETE FROM students WHERE 1=1'
            params = []
            
            # Те же условия, что и в search_students
            if criteria.get('student_name'):
                condition, cond_params = self.build_name_condition(
                    criteria['student_name'], 'student_name'
                )
                if condition:
                    query += f" AND ({condition})"
                    params.extend(cond_params)
            
            if criteria.get('father_name'):
                condition, cond_params = self.build_name_condition(
                    criteria['father_name'], 'father_name'
                )
                if condition:
                    query += f" AND ({condition})"
                    params.extend(cond_params)
            
            if criteria.get('mother_name'):
                condition, cond_params = self.build_name_condition(
                    criteria['mother_name'], 'mother_name'
                )
                if condition:
                    query += f" AND ({condition})"
                    params.extend(cond_params)
            
            if criteria.get('brothers') is not None:
                query += " AND brothers = ?"
                params.append(criteria['brothers'])
            
            if criteria.get('sisters') is not None:
                query += " AND sisters = ?"
                params.append(criteria['sisters'])
            
            if criteria.get('father_income_min') is not None:
                query += " AND father_income >= ?"
                params.append(criteria['father_income_min'])
            
            if criteria.get('father_income_max') is not None:
                query += " AND father_income <= ?"
                params.append(criteria['father_income_max'])
            
            if criteria.get('mother_income_min') is not None:
                query += " AND mother_income >= ?"
                params.append(criteria['mother_income_min'])
            
            if criteria.get('mother_income_max') is not None:
                query += " AND mother_income <= ?"
                params.append(criteria['mother_income_max'])
            
            self.cursor.execute(query, params)
            self.connection.commit()
        
        return count
    
    def clear_all(self):
        """Очищает таблицу (для тестирования)"""
        self.cursor.execute('DELETE FROM students')
        self.connection.commit()
    
    def __del__(self):
        """Деструктор для закрытия соединения"""
        self.disconnect()