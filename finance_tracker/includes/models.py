## Model for Transactions
from datetime import date

class Transactions:
    def __init__(self, amount: float, category: str, type_: str, date_: date = None, notes: str = ""):
        self.amount = amount
        self.category = category
        self.type = type_.lower()  # 'income' or 'expense'
        self.date = date_ if date_ else date.today()
        self.notes = notes

    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "date": self.date.isoformat(),
            "notes": self.notes
        } 
    
    def __repr__(self):
        return f"<{self.type.capitalize()} {self.amount} in '{self.category}' on {self.date}>"