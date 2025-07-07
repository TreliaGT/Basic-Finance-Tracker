import tkinter as tk
from tkinter import ttk
from datetime import datetime, date

from includes.models import Transactions
from includes.db import add_transaction, close_connection, remove_transaction , get_all_transactions


class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x500")
        self.root.title("Finance Tracker")

        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    #base layout
    def setup_ui(self):
        self.sidebar = tk.Frame(self.root, width=150, bg="lightgray")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.main_box = tk.Frame(self.root, bg="white")
        self.main_box.pack(side="left", fill="both", expand=True)

        # --- Sidebar widgets ---
        self.amount_var = tk.StringVar()
        self._add_labeled_entry(self.sidebar, "Amount:", self.amount_var)

        self.category_var = tk.StringVar()
        self._add_labeled_entry(self.sidebar, "Category:", self.category_var)

        self.type_var = tk.StringVar(value="income")
        self._add_labeled_dropdown(self.sidebar, "Type:", self.type_var, ["income", "expense"])

        self.date_var = tk.StringVar(value=str(date.today()))
        self._add_labeled_entry(self.sidebar, "Date:", self.date_var)

        tk.Label(self.sidebar, text="Notes:", bg="lightgray", anchor="w").pack(pady=(10, 0), padx=10, anchor="w")
        self.notes_text = tk.Text(self.sidebar, height=4, width=18)
        self.notes_text.pack(padx=10, pady=(0, 10))

        self.add_btn = tk.Button(self.sidebar, text="Add Transations" , command=self.add_transaction)
        self.add_btn.pack(padx=10, pady=(0, 10))

        # --- Main box ---
        self.message_var = tk.Message(self.main_box, text="No transactions to display yet.")
        self.message_var.config(bg='red', fg='white', width=400)
        self.message_var.pack(padx=10, pady=10)

        self._setup_action_frame()
        self._setup_treeview()
        self.load_all_transactions()

    # set up labed entries
    def _add_labeled_entry(self, parent, text, variable):
        tk.Label(parent, text=text, bg="lightgray", anchor="w").pack(pady=(10, 0), padx=10, anchor="w")
        tk.Entry(parent, textvariable=variable, width=20).pack(padx=10)

    # Set up Drop down
    def _add_labeled_dropdown(self, parent, text, variable, values):
        tk.Label(parent, text=text, bg="lightgray", anchor="w").pack(pady=(10, 0), padx=10, anchor="w")
        ttk.Combobox(parent, textvariable=variable, values=values, state="readonly", width=17).pack(padx=10)

    # set up the action bar
    def _setup_action_frame(self):
        action_frame = tk.Frame(self.main_box, bg="white")
        action_frame.pack(pady=(0, 10))

        delete_button = tk.Button(action_frame, text="Delete", bg='red', fg='white' , command=self.delete_selected)
        delete_button.grid(row=0, column=7, padx=5)  

        export_button = tk.Button(action_frame, text="Export", bg='green', fg='white')
        export_button.grid(row=0, column=8, padx=5)  

        dummy_button = tk.Button(action_frame, text="Dummy", bg='blue', fg='white' , command=self.dummy_data)
        dummy_button.grid(row=0, column=9, padx=5)  

        tk.Label(action_frame, text="Category:", bg="white").grid(row=0, column=0, padx=5, sticky="e")
        self.search_category = tk.StringVar()
        tk.Entry(action_frame, textvariable=self.search_category, width=20).grid(row=0, column=1, padx=5)

        tk.Label(action_frame, text="Start Date:", bg="white").grid(row=0, column=2, padx=5, sticky="e")
        self.start_search_date = tk.StringVar()
        tk.Entry(action_frame, textvariable=self.start_search_date, width=20).grid(row=0, column=3, padx=5)

        tk.Label(action_frame, text="End Date:", bg="white").grid(row=0, column=4, padx=5, sticky="e")
        self.end_search_date = tk.StringVar()
        tk.Entry(action_frame, textvariable=self.end_search_date, width=20).grid(row=0, column=5, padx=5)

        search_button = tk.Button(action_frame, text="Search", command=self.search_transactions)
        search_button.grid(row=0, column=6, padx=5) 

    #set up tree view
    def _setup_treeview(self):
        columns = ("date", "type", "amount", "category", "notes")
        self.tree = ttk.Treeview(self.main_box, columns=columns, show="headings")

        for col in columns:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sort_by_column(c, False))
            self.tree.column(col, width=100 if col == "date" else 80 if col in ["type", "amount"] else 200)

        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

    #Sorts the table by column
    def sort_by_column(self, col, reverse):
        data = [(self.tree.set(child, col), child) for child in self.tree.get_children()]

        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
            if col == "date":
                data.sort(key=lambda t: datetime.strptime(t[0], "%Y-%m-%d"), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0].lower(), reverse=reverse)

        for index, (val, child) in enumerate(data):
            self.tree.move(child, '', index)

        self.tree.heading(col, command=lambda: self.sort_by_column(col, not reverse))

    #Load All
    def load_all_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_transactions = get_all_transactions()
        for trans in all_transactions:
            trans_id, amount, category, trans_type, trans_date, notes = trans
            self.tree.insert("", "end", iid=str(trans_id), values=(trans_date, trans_type, f"{amount:.2f}", category, notes))


    #Delete
    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.message_var.config(text="No transaction selected to delete.", bg='red')
            return

        for item_id in selected_items:
            # Delete from DB using item_id as the transaction id
            remove_transaction(int(item_id))
            # Delete from treeview
            self.tree.delete(item_id)

        self.message_var.config(text=f"Deleted {len(selected_items)} transaction(s).", bg='green')

    #add
    def add_transaction(self):
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            self.message_var.config(text="Invalid amount!", bg='red')
            return

        category = self.category_var.get().strip()
        if not category:
            self.message_var.config(text="Category cannot be empty!", bg='red')
            return

        trans_type = self.type_var.get()
        trans_date = self.date_var.get().strip()
        notes = self.notes_text.get("1.0", "end").strip()

        # Validate date format (simple check)
        try:
            date_obj = datetime.strptime(trans_date, "%Y-%m-%d").date()
        except ValueError:
            self.message_var.config(text="Invalid date format! Use YYYY-MM-DD.", bg='red')
            return

        # Create a transaction instance
        transaction = Transactions(amount, category, trans_type, date_obj, notes)

        # Add to DB
        trans_id = add_transaction(transaction)

        # Update UI
        self.message_var.config(text="Transaction added successfully.", bg='green')

        # Insert into treeview
        self.tree.insert("", "end", iid=str(trans_id), values=(trans_date, trans_type, f"{amount:.2f}", category, notes))


        # Clear inputs
        self.amount_var.set("")
        self.category_var.set("")
        self.type_var.set("income")
        self.date_var.set(str(date.today()))
        self.notes_text.delete("1.0", "end")

    #search
    def search_transactions(self):
        category_search = self.search_category.get().strip().lower()
        start_date_str = self.start_search_date.get().strip()
        end_date_str = self.end_search_date.get().strip()

        # Clear treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        all_transactions = get_all_transactions()  # List of tuples

        filtered = []
        for trans in all_transactions:
            trans_id, amount, category, trans_type, trans_date, notes = trans

            # Filter by category
            if category_search and category_search not in category.lower():
                continue

            # Filter by date range
            try:
                trans_date_obj = datetime.strptime(trans_date, '%Y-%m-%d').date()
            except ValueError:
                continue  # Skip invalid dates

            if start_date_str:
                try:
                    start_date_obj = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    if trans_date_obj < start_date_obj:
                        continue
                except ValueError:
                    pass  # Invalid start date input — ignore filtering

            if end_date_str:
                try:
                    end_date_obj = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    if trans_date_obj > end_date_obj:
                        continue
                except ValueError:
                    pass  # Invalid end date input — ignore filtering

            filtered.append((trans_id, trans_date, trans_type, str(amount), category, notes))

        # Show message
        if not filtered:
            self.message_var.config(text="No transactions found.", bg='red')
        else:
            self.message_var.config(text=f"Found {len(filtered)} transactions.", bg='green')

        # Insert filtered rows into Treeview
        for trans_id, trans_date, trans_type, amount, category, notes in filtered:
            self.tree.insert("", "end", iid=str(trans_id), values=(trans_date, trans_type, amount, category, notes))
        
    def on_closing(self):
        close_connection()
        self.root.destroy()

    def dummy_data(self):
        dummy_transactions = [
            Transactions(150.00, "Salary", "income", date(2024, 1, 5), "January salary"),
            Transactions(75.50, "Groceries", "expense", date(2024, 1, 10), "Weekly grocery shopping"),
            Transactions(20.00, "Transport", "expense", date(2024, 1, 11), "Bus ticket"),
            Transactions(250.00, "Freelance", "income", date(2024, 1, 15), "Project payment"),
            Transactions(60.00, "Utilities", "expense", date(2024, 1, 17), "Electricity bill"),
            Transactions(40.00, "Dining Out", "expense", date(2024, 1, 18), "Dinner with friends"),
            Transactions(100.00, "Gift", "expense", date(2024, 1, 20), "Birthday gift"),
            Transactions(500.00, "Bonus", "income", date(2024, 1, 25), "Year-end bonus"),
            Transactions(35.00, "Subscription", "expense", date(2024, 2, 1), "Streaming service"),
            Transactions(120.00, "Freelance", "income", date(2024, 2, 5), "Logo design"),
            Transactions(200.00, "Rent", "expense", date(2024, 2, 1), "February rent"),
            Transactions(15.00, "Coffee", "expense", date(2024, 2, 7), "Coffee shop"),
            Transactions(80.00, "Shopping", "expense", date(2024, 2, 10), "Clothes shopping"),
            Transactions(300.00, "Investment", "income", date(2024, 2, 12), "Stock dividends"),
            Transactions(50.00, "Medical", "expense", date(2024, 2, 15), "Doctor appointment"),
        ]

        for transaction in dummy_transactions:
            trans_id = add_transaction(transaction)
            # Insert into treeview
            self.tree.insert("", "end", iid=str(trans_id), values=(transaction.date, transaction.type, f"{transaction.amount:.2f}", transaction.category, transaction.notes))