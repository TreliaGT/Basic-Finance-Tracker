## Database
import sqlite3

conn = sqlite3.connect('data/transactions.db') 
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('income', 'expense' , 'unknown')),
    date TEXT NOT NULL,
    notes TEXT
)
''')

conn.commit()

# Get ALL 
def get_all_transactions():
    cursor.execute('SELECT id, amount, category, type, date, notes FROM transactions')
    rows = cursor.fetchall()
    # Return rows as list of tuples or you can convert to objects
    return rows

#add new
def add_transaction(transaction):
    cursor.execute('''
        INSERT INTO transactions (amount, category, type, date, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        transaction.amount,
        transaction.category,
        transaction.type,
        transaction.date.isoformat(),
        transaction.notes
    ))
    conn.commit()
    return cursor.lastrowid 

#remove 
def remove_transaction(transaction_id: int):
    cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
    conn.commit()

#close the connection
def close_connection():
    cursor.close()
    conn.close()