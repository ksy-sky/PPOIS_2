class TeachingMaterial:
    def __init__(self, title: str, quantity: int):
        if quantity < 0:
            raise ValueError("Количество не может быть отрицательным")
        
        self.title = title
        self.quantity = quantity
    
    def use(self, amount: int = 1) -> None:
        if amount > self.quantity:
            raise ValueError(f"Не хватает {self.title}! Есть {self.quantity}, нужно {amount}")
        
        self.quantity -= amount
    
    def __str__(self) -> str:
        return f"{self.title} (осталось: {self.quantity})"
    
    def to_dict(self) -> dict:
        return {"title": self.title, "quantity": self.quantity}
    
    @classmethod
    def from_dict(cls, data: dict) -> "TeachingMaterial":
        return cls(data["title"], data["quantity"])