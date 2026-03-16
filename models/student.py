class Student:
    """Модель данных студента"""
    
    def __init__(self, id=None, student_name="", father_name="", father_income=0.0,
                 mother_name="", mother_income=0.0, brothers=0, sisters=0):
        self.id = id  # id из базы данных (None для новых записей)
        self.student_name = student_name
        self.father_name = father_name
        self.father_income = float(father_income)  # гарантируем float
        self.mother_name = mother_name
        self.mother_income = float(mother_income)
        self.brothers = int(brothers)  # гарантируем int
        self.sisters = int(sisters)
    
    def __str__(self):
        return f"Студент: {self.student_name}"
    
    def to_tuple(self):
        """Преобразует объект в кортеж для вставки в БД"""
        return (self.student_name, self.father_name, self.father_income,
                self.mother_name, self.mother_income, self.brothers, self.sisters)
    
    @classmethod
    def from_tuple(cls, data_tuple, id=None):
        """Создает объект Student из кортежа данных"""
        if id is None and len(data_tuple) == 8:  # если id включен в кортеж
            id = data_tuple[0]
            data = data_tuple[1:]
        else:
            data = data_tuple
        
        return cls(
            id=id,
            student_name=data[0],
            father_name=data[1],
            father_income=data[2],
            mother_name=data[3],
            mother_income=data[4],
            brothers=data[5],
            sisters=data[6]
        )