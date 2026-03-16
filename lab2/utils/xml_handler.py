#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
XML обработчик для сохранения (DOM) и загрузки (SAX)
"""

import xml.dom.minidom as minidom
import xml.sax
from xml.sax.handler import ContentHandler
from models.student import Student

class XMLExport:
    """Экспорт данных в XML с использованием DOM парсера"""
    
    @staticmethod
    def save_to_file(students, filename):
        """
        Сохраняет список студентов в XML файл
        Использует DOM парсер
        """
        # Создаем корневой элемент
        doc = minidom.Document()
        root = doc.createElement("students")
        doc.appendChild(root)
        
        for student in students:
            # Создаем элемент для студента
            student_elem = doc.createElement("student")
            
            # Добавляем поля
            fields = [
                ("student_name", student.student_name),
                ("father_name", student.father_name),
                ("father_income", str(student.father_income)),
                ("mother_name", student.mother_name),
                ("mother_income", str(student.mother_income)),
                ("brothers", str(student.brothers)),
                ("sisters", str(student.sisters))
            ]
            
            for tag, value in fields:
                elem = doc.createElement(tag)
                elem.appendChild(doc.createTextNode(value))
                student_elem.appendChild(elem)
            
            root.appendChild(student_elem)
        
        # Записываем в файл с красивым форматированием
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(doc.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8'))
        
        return True

class XMLImportHandler(ContentHandler):
    """Обработчик для SAX парсера - читает XML и создает студентов"""
    
    def __init__(self):
        super().__init__()
        self.students = []
        self.current_student = None
        self.current_tag = ""
        self.current_value = ""
        
        # Соответствие тегов и атрибутов
        self.field_map = {
            "student_name": "student_name",
            "father_name": "father_name",
            "father_income": "father_income",
            "mother_name": "mother_name",
            "mother_income": "mother_income",
            "brothers": "brothers",
            "sisters": "sisters"
        }
    
    def startElement(self, tag, attrs):
        """Начало элемента"""
        self.current_tag = tag
        self.current_value = ""
        
        if tag == "student":
            self.current_student = {}
    
    def characters(self, content):
        """Текстовое содержимое элемента"""
        self.current_value += content
    
    def endElement(self, tag):
        """Конец элемента"""
        if tag == "student":
            # Создаем студента из накопленных данных
            if self.current_student:
                try:
                    student = Student(
                        student_name=self.current_student.get("student_name", ""),
                        father_name=self.current_student.get("father_name", ""),
                        father_income=float(self.current_student.get("father_income", 0)),
                        mother_name=self.current_student.get("mother_name", ""),
                        mother_income=float(self.current_student.get("mother_income", 0)),
                        brothers=int(self.current_student.get("brothers", 0)),
                        sisters=int(self.current_student.get("sisters", 0))
                    )
                    self.students.append(student)
                except (ValueError, TypeError) as e:
                    print(f"Ошибка при создании студента: {e}")
            self.current_student = None
        
        elif tag in self.field_map and self.current_student is not None:
            # Сохраняем значение поля
            field_name = self.field_map[tag]
            self.current_student[field_name] = self.current_value.strip()
        
        self.current_tag = ""
    
    def get_students(self):
        """Возвращает список загруженных студентов"""
        return self.students

class XMLImport:
    """Импорт данных из XML с использованием SAX парсера"""
    
    @staticmethod
    def load_from_file(filename):
        """
        Загружает студентов из XML файла
        Использует SAX парсер
        """
        handler = XMLImportHandler()
        
        try:
            # Создаем SAX парсер
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            
            # Парсим файл
            parser.parse(filename)
            
            return handler.get_students()
            
        except Exception as e:
            raise Exception(f"Ошибка при загрузке XML: {str(e)}")

# Пример использования (для теста)
if __name__ == "__main__":
    # Создаем тестовых студентов
    from models.student import Student
    
    students = [
        Student(
            student_name="Иванов Иван Иванович",
            father_name="Иванов Иван Петрович",
            father_income=50000.50,
            mother_name="Иванова Мария Сидоровна",
            mother_income=45000.75,
            brothers=1,
            sisters=0
        ),
        Student(
            student_name="Петров Петр Петрович",
            father_name="Петров Петр Иванович",
            father_income=60000.00,
            mother_name="Петрова Ольга Сергеевна",
            mother_income=55000.25,
            brothers=0,
            sisters=2
        )
    ]
    
    # Сохраняем
    print("Сохраняем в XML...")
    XMLExport.save_to_file(students, "test.xml")
    
    # Загружаем
    print("Загружаем из XML...")
    loaded = XMLImport.load_from_file("test.xml")
    
    print(f"Загружено студентов: {len(loaded)}")
    for s in loaded:
        print(f"  - {s.student_name}")