import tkinter as tk
from views.ui import FinanceTrackerApp

# Create a transaction instance
#t1 = Transations(amount=50.0, category="Groceries", type_="Expense", notes="Weekly shopping")

def main():
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()