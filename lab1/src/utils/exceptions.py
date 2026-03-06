class KindergartenException(Exception):
    """Базовое исключение для всех ошибок детского сада"""
    pass

class ChildNotFoundError(KindergartenException):
    """Выбрасывается, если ребенок с таким именем не найден"""
    pass

class InvalidAgeError(KindergartenException):
    """Выбрасывается, если возраст ребенка недопустим (меньше 1 или больше 7)"""
    pass

class ParentNotFoundError(KindergartenException):
    """Выбрасывается, если у ребенка нет родителя"""
    pass

class GameNotFoundError(KindergartenException):
    """Выбрасывается, если игра не найдена"""
    pass

class MaterialNotFoundError(KindergartenException):
    """Выбрасывается, если материал не найден"""
    pass

class InvalidStateError(KindergartenException):
    """Выбрасывается при попытке недопустимого действия с ребенком"""
    pass

class GameAgeError(KindergartenException):
    """Выбрасывается, если игра не подходит ребенку по возрасту"""
    pass

class SaveError(KindergartenException):
    """Выбрасывается при ошибке сохранения"""
    pass

class GroupError(KindergartenException):
    """Выбрасывается при ошибках, связанных с группами"""
    pass

class LoadError(KindergartenException):
    """Выбрасывается при ошибке загрузки"""
    pass