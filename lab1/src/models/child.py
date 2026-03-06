from src.utils.exceptions import InvalidStateError, InvalidAgeError

    
class Child:
    
    # Возможные состояния ребенка (константа)
    VALID_STATES = ["hungry", "awake", "playing", "sleeping", "left"]
        # Допустимый возраст для детского сада
    MIN_AGE = 1
    MAX_AGE = 7

           # Создание нового ребенка, initial_state: начальное состояние (по умолчанию "left")
    def __init__(self, name: str, age: int, initial_state: str = "left"):
        # Проверяем типы данных
        if not isinstance(name, str):
            raise TypeError("Имя должно быть строкой")
        
        if not isinstance(age, int):
            raise TypeError("Возраст должен быть целым числом")
        
        # Проверка возраста
        if age < self.MIN_AGE or age > self.MAX_AGE:
            raise InvalidAgeError(
                f"Возраст {age} недопустим для детского сада. "
                f"Допустимый возраст: от {self.MIN_AGE} до {self.MAX_AGE} лет"
            )
        if initial_state not in self.VALID_STATES:
            raise InvalidStateError(f"Недопустимое состояние: {initial_state}")         
        # Сохраняем данные
        self.name = name
        self.age = age
        self._state = initial_state #Почему _state с подчёркиванием?
# Это сигнал программисту: «Не меняй эту переменную напрямую!». Меняй только через специальный метод.
    def make_hungry(self):
        if self.state in ["awake", "playing"]:
            self._state = "hungry"
            print(f"  {self.name} проголодался!")
            return True
        else:
            raise InvalidStateError(f"Нельзя сделать {self.name} голодным (сейчас {self.state})")
        
    @property #getter (позволяет читать state, но не менять напрямую)
    def state(self) -> str: #метод возвращает строку, можно без этой херни но РЕР8
        return self._state
        
    def update_state(self, new_state: str) -> None:
        if new_state not in self.VALID_STATES:
            raise InvalidStateError(f"Нельзя перевести {self.name} в состояние {new_state}")
        self._state = new_state
        print(f"{self.name} теперь {new_state}")
    
    def __str__(self) -> str: # Строковое представление ребенка\ или показывало бы фигню   
        return f"{self.name} ({self.age} лет) - {self._state}"

    def to_dict(self) -> dict:
       # Преобразовать в словарь для сохранения, файл JSON
        return {
            "name": self.name,
            "age": self.age,
            "state": self._state
        }
    
    @classmethod #метод работает с классом а не объектом
    def from_dict(cls, data: dict) -> "Child": # cls как селф но для класса\ ссылка на класс
        return cls(data["name"], data["age"], data["state"])