import pandas as pd
import sqlite3

def export_transactions_to_excel(db_path='transactions.db', output_file='transactions_export.xlsx'):
    # Connect to your SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all transactions
    cursor.execute("SELECT * FROM transactions")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]

    # Convert to DataFrame and export
    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(output_file, index=False)

    print(f"✅ Transactions exported to {output_file}")

    # Clean up
    cursor.close()
    conn.close()
