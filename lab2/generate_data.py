#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Скрипт для генерации 50+ тестовых данных
Запуск: python3 generate_test_data.py
"""

import random
import os
from models.database import Database
from models.student import Student

# Фамилии (30 штук - хватит для 50 студентов)
surname_bases = [
    "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов", "Васильев",
    "Павлов", "Соколов", "Михайлов", "Федоров", "Морозов", "Волков", "Алексеев",
    "Лебедев", "Семенов", "Егоров", "Козлов", "Степанов", "Николаев", "Орлов",
    "Андреев", "Макаров", "Никитин", "Захаров", "Зайцев", "Соловьев", "Борисов",
    "Яковлев", "Григорьев"
]

# Имена (мужские)
male_names = [
    "Александр", "Дмитрий", "Максим", "Сергей", "Андрей", "Алексей", "Иван",
    "Евгений", "Михаил", "Николай", "Владимир", "Павел", "Артем", "Денис",
    "Виктор", "Игорь", "Олег", "Роман", "Вадим", "Константин"
]

# Имена (женские)
female_names = [
    "Елена", "Ольга", "Наталья", "Татьяна", "Ирина", "Светлана", "Марина",
    "Анна", "Юлия", "Екатерина", "Анастасия", "Ксения", "Виктория", "Дарья",
    "Мария", "Евгения", "Надежда", "Людмила", "Галина", "Александра"
]

def get_patronymic(father_name, child_gender="male"):
    """Образует отчество от имени отца"""
    # Особые случаи
    if father_name == "Павел":
        return "Павлович" if child_gender == "male" else "Павловна"
    elif father_name == "Игорь":
        return "Игоревич" if child_gender == "male" else "Игоревна"
    elif father_name == "Михаил":
        return "Михайлович" if child_gender == "male" else "Михайловна"
    elif father_name == "Александр":
        return "Александрович" if child_gender == "male" else "Александровна"
    elif father_name == "Андрей":
        return "Андреевич" if child_gender == "male" else "Андреевна"
    elif father_name == "Дмитрий":
        return "Дмитриевич" if child_gender == "male" else "Дмитриевна"
    elif father_name == "Евгений":
        return "Евгеньевич" if child_gender == "male" else "Евгеньевна"
    elif father_name == "Юрий":
        return "Юрьевич" if child_gender == "male" else "Юрьевна"
    elif father_name == "Алексей":
        return "Алексеевич" if child_gender == "male" else "Алексеевна"
    elif father_name == "Сергей":
        return "Сергеевич" if child_gender == "male" else "Сергеевна"
    elif father_name == "Николай":
        return "Николаевич" if child_gender == "male" else "Николаевна"
    elif father_name == "Владимир":
        return "Владимирович" if child_gender == "male" else "Владимировна"
    
    # Общий случай
    if father_name.endswith("й"):
        base = father_name[:-1]
        return base + ("евич" if child_gender == "male" else "евна")
    else:
        return father_name + ("ович" if child_gender == "male" else "овна")

def get_female_surname(surname):
    """Образует женскую фамилию от мужской"""
    if surname.endswith("ов"):
        return surname[:-2] + "ова"
    elif surname.endswith("ев"):
        return surname[:-2] + "ева"
    elif surname.endswith("ин"):
        return surname[:-2] + "ина"
    else:
        return surname + "а"

def generate_family():
    """Генерирует одну семью"""
    # Выбираем уникальную фамилию
    surname_base = random.choice(surname_bases)
    
    # Отец
    father_first = random.choice(male_names)
    father_patronymic = get_patronymic(random.choice(male_names), "male")
    father_full = f"{surname_base} {father_first} {father_patronymic}"
    
    # Мать
    mother_first = random.choice(female_names)
    mother_father = random.choice(male_names)
    mother_patronymic = get_patronymic(mother_father, "female")
    mother_full = f"{get_female_surname(surname_base)} {mother_first} {mother_patronymic}"
    
    # Зарплаты
    father_income = round(random.uniform(30000, 200000), 2)
    mother_income = round(random.uniform(25000, 150000), 2)
    
    # 1-3 детей
    children_count = random.randint(1, 3)
    children = []
    child_genders = [random.choice(["male", "female"]) for _ in range(children_count)]
    
    for i in range(children_count):
        gender = child_genders[i]
        
        # Имя ребенка
        if gender == "male":
            child_first = random.choice([n for n in male_names if n != father_first][:5])
            child_surname = surname_base
        else:
            child_first = random.choice([n for n in female_names if n != mother_first][:5])
            child_surname = get_female_surname(surname_base)
        
        # Отчество
        child_patronymic = get_patronymic(father_first, gender)
        
        child_full = f"{child_surname} {child_first} {child_patronymic}"
        
        # Братья и сестры
        brothers = sum(1 for j, g in enumerate(child_genders) if j != i and g == "male")
        sisters = sum(1 for j, g in enumerate(child_genders) if j != i and g == "female")
        
        children.append(Student(
            student_name=child_full,
            father_name=father_full,
            father_income=father_income,
            mother_name=mother_full,
            mother_income=mother_income,
            brothers=brothers,
            sisters=sisters
        ))
    
    return children

def generate_students(target_count=55):
    """Генерирует 55 студентов (чуть больше 50)"""
    students = []
    used_surnames = set()
    
    print("Генерация студентов...")
    
    while len(students) < target_count:
        # Выбираем фамилию, которой еще не было или редко использовали
        available = [s for s in surname_bases if s not in used_surnames]
        if available:
            surname = random.choice(available)
            used_surnames.add(surname)
        else:
            surname = random.choice(surname_bases)
        
        family = generate_family()
        
        # Оставляем 1-2 студента из семьи
        keep_count = random.randint(1, min(2, len(family)))
        selected = random.sample(family, keep_count)
        students.extend(selected)
        
        if len(students) % 10 == 0:
            print(f"  {len(students)} студентов...")
    
    students = students[:target_count]
    print(f"\n✅ Сгенерировано {len(students)} студентов")
    return students

def save_to_xml(students, filename):
    """Сохраняет данные в XML"""
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    
    root = ET.Element("students")
    
    for student in students:
        s = ET.SubElement(root, "student")
        ET.SubElement(s, "student_name").text = student.student_name
        ET.SubElement(s, "father_name").text = student.father_name
        ET.SubElement(s, "father_income").text = str(student.father_income)
        ET.SubElement(s, "mother_name").text = student.mother_name
        ET.SubElement(s, "mother_income").text = str(student.mother_income)
        ET.SubElement(s, "brothers").text = str(student.brothers)
        ET.SubElement(s, "sisters").text = str(student.sisters)
    
    xml_str = ET.tostring(root, encoding='utf-8')
    dom = minidom.parseString(xml_str)
    pretty = dom.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(pretty)

def main():
    print("=" * 50)
    print("ГЕНЕРАЦИЯ 50+ ТЕСТОВЫХ ДАННЫХ")
    print("=" * 50)
    
    # Создаем папку data
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Очищаем БД
    db = Database("data/students.db")
    db.clear_all()
    
    # Генерируем 55 студентов
    students = generate_students(55)
    
    # Сохраняем в БД
    for student in students:
        db.add_student(student)
    
    print(f"\n💾 В БД добавлено: {db.get_total_count()} записей")
    
    # Сохраняем в XML (2 файла)
    save_to_xml(students, "data/students_set1.xml")
    print("📄 data/students_set1.xml")
    
    # Еще один набор
    students2 = generate_students(52)
    save_to_xml(students2, "data/students_set2.xml")
    print("📄 data/students_set2.xml")
    
    print("\n" + "=" * 50)
    print("ГОТОВО! Всего создано:")
    print(f"  • {len(students)} + {len(students2)} = {len(students) + len(students2)} студентов")
    print("  • 2 XML файла")
    print("=" * 50)

if __name__ == "__main__":
    main()