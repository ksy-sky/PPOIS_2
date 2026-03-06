from src.utils.exceptions import InvalidStateError

class Parent:
    def __init__(self, name: str, child):
        self.name = name
        self.child = child
    
    def drop_off(self) -> dict:
        if self.child.state == "left": #дома
            self.child.update_state("hungry")
            return {
                "success": True,
                "message": f"{self.name} привел(а) {self.child.name} в сад (он голоден)"
            }
        else:
            raise InvalidStateError(f"{self.child.name} уже в саду")
    
    def pickup(self) -> dict:
        if self.child.state != "left":
            self.child.update_state("left")
            return {
                "success": True,
                "message": f"{self.name} забрал(а) {self.child.name} домой"
            }
        else:
            raise InvalidStateError(f"{self.child.name} уже дома")
    
    def to_dict(self) -> dict: #Для сохранения
        return {
            "name": self.name,
            "child_name": self.child.name
        }
    @classmethod
    def from_dict(cls, data: dict, child) -> "Parent":
        """Загрузка из словаря с привязкой к ребенку"""
        return cls(data["name"], child)