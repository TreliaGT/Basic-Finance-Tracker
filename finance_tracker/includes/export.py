import pandas as pd

def export_transactions_to_excel(treeview, output_file='transactions_export.xlsx', message_callback=None):
    """
    Export transactions from a given Treeview widget to an Excel file.
    
    Parameters:
    - treeview: ttk.Treeview instance containing the transactions.
    - output_file: filename to save the Excel file.
    - message_callback: optional function to send messages (like success or errors).
    """
    transactions = []
    for item_id in treeview.get_children():
        row = treeview.item(item_id)['values']
        transactions.append({
            "Date": row[0],
            "Type": row[1],
            "Amount": row[2],
            "Category": row[3],
            "Notes": row[4]
        })

    if not transactions:
        if message_callback:
            message_callback("No transactions to export.", "red")
        return
    
    df = pd.DataFrame(transactions)
    try:
        df.to_excel(output_file, index=False)
        if message_callback:
            message_callback(f"Transactions exported to {output_file}", "green")
    except Exception as e:
        if message_callback:
            message_callback(f"Error exporting: {e}", "red")
