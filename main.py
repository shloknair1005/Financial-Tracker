import sqlite3
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import matplotlib.pyplot as plt
from tkinter import messagebox


def create_db():
    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                     id INTEGER PRIMARY KEY AUTOINCREMENT,
                     description TEXT NOT NULL,
                     amount REAL NOT NULL,
                     date TEXT NOT NULL)''')
    conn.commit()
    conn.close()

create_db()


def validate_date(date_text):
    try:
        datetime.strptime(date_text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def add_transaction():
    desc = description_var.get()
    amount = amount_var.get()
    date = date_var.get()

    if not desc or not amount or not date:
        message_label.config(text="Error: Please fill out all fields", fg="red")
        return

    if not validate_date(date):
        message_label.config(text="Error: Date must be in YYYY-MM-DD format", fg="red")
        return

    try:
        amount = float(amount)
    except ValueError:
        message_label.config(text="Error: Amount must be a number", fg="red")
        return

    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute('INSERT INTO transactions (description, amount, date) VALUES (?, ?, ?)', (desc, amount, date))
    conn.commit()
    conn.close()


    description_var.set("")
    amount_var.set("")
    date_var.set(datetime.now().strftime("%Y-%m-%d"))

    
    message_label.config(text="Transaction added successfully", fg="green")


def show_daily_summary():
    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute('SELECT date, SUM(amount) FROM transactions GROUP BY date ORDER BY date')
    data = c.fetchall()
    conn.close()

    dates = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.bar(dates, amounts, color='red')
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.title('Daily Expenses', fontsize=16)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def show_monthly_summary():
    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute("SELECT strftime('%Y-%m', date) AS month, SUM(amount) FROM transactions GROUP BY month ORDER BY month")
    data = c.fetchall()
    conn.close()

    months = [row[0] for row in data]
    amounts = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.bar(months, amounts, color='blue')
    plt.xlabel('Month', fontsize=12)
    plt.ylabel('Amount', fontsize=12)
    plt.title('Monthly Expenses', fontsize=16)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def delete_transaction(transaction_id):
    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()
    conn.close()
    show_transactions_list()  


def edit_transaction(transaction_id):
    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute("SELECT description, amount, date FROM transactions WHERE id=?", (transaction_id,))
    transaction = c.fetchone()
    conn.close()

    if transaction:
        description_var.set(transaction[0])
        amount_var.set(str(transaction[1]))
        date_var.set(transaction[2])

        def update_transaction():
            desc = description_var.get()
            amount = amount_var.get()
            date = date_var.get()

            if not desc or not amount or not date:
                messagebox.showerror("Error", "Please fill out all fields")
                return

            if not validate_date(date):
                messagebox.showerror("Error", "Date must be in YYYY-MM-DD format")
                return

            try:
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
                return

            conn = sqlite3.connect('finance_tracker.db')
            c = conn.cursor()
            c.execute('UPDATE transactions SET description=?, amount=?, date=? WHERE id=?',
                      (desc, amount, date, transaction_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Transaction updated successfully")
            show_transactions_list()

        add_button.config(text="Update Transaction", command=update_transaction)


def show_transactions_list():
    list_window = tk.Toplevel(root)
    list_window.title("Transactions List")

    tree = ttk.Treeview(list_window, columns=("ID", "Date", "Description", "Amount"), show="headings", height=15)
    tree.heading("ID", text="ID")
    tree.heading("Date", text="Date")
    tree.heading("Description", text="Description")
    tree.heading("Amount", text="Amount")
    tree.column("ID", width=30)
    tree.column("Date", width=100)
    tree.column("Description", width=200)
    tree.column("Amount", width=80)
    tree.grid(row=0, column=0, padx=10, pady=10)

    scrollbar = ttk.Scrollbar(list_window, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=0, column=1, sticky='ns')

    conn = sqlite3.connect('finance_tracker.db')
    c = conn.cursor()
    c.execute("SELECT id, date, description, amount FROM transactions ORDER BY date")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        tree.insert("", tk.END, values=row)

    def on_item_selected(event):
        selected_item = tree.selection()[0]
        transaction_id = tree.item(selected_item, 'values')[0]
        edit_button = tk.Button(list_window, text="Edit", command=lambda: edit_transaction(transaction_id))
        delete_button = tk.Button(list_window, text="Delete", command=lambda: delete_transaction(transaction_id))
        edit_button.grid(row=1, column=0, padx=10, pady=5, sticky='w')
        delete_button.grid(row=1, column=0, padx=10, pady=5, sticky='e')

    tree.bind('<<TreeviewSelect>>', on_item_selected)


def toggle_fullscreen():
    if root.attributes('-fullscreen'):
        root.attributes('-fullscreen', False)
    else:
        root.attributes('-fullscreen', True)


def open_calculator():
    calc_window = tk.Toplevel(root)
    calc_window.title("Calculator")
    calc_window.config(bg="#f0f0f0")

    calc_input = tk.Entry(calc_window, width=20, font=("Arial", 24), bd=10, insertwidth=4, justify="right", bg="#e6f7ff")
    calc_input.grid(row=0, column=0, columnspan=4)

    def button_click(item):
        current = calc_input.get()
        calc_input.delete(0, tk.END)
        calc_input.insert(0, current + str(item))

    def button_clear():
        calc_input.delete(0, tk.END)

    def button_equal():
        try:
            result = str(eval(calc_input.get()))
            calc_input.delete(0, tk.END)
            calc_input.insert(0, result)
        except:
            calc_input.delete(0, tk.END)
            calc_input.insert(0, "Error")

    def button_remove():
        current = calc_input.get()
        calc_input.delete(0, tk.END)
        calc_input.insert(0, current[:-1])

    buttons = [
        '7', '8', '9', '/', 
        '4', '5', '6', '*', 
        '1', '2', '3', '-', 
        'C', '0', 'Del', '=', '+'
    ]

    row_val = 1
    col_val = 0
    for button in buttons:
        if button == "=":
            btn = tk.Button(calc_window, text=button, padx=20, pady=20, font=("Arial", 18), bg="lightgreen",
                            command=button_equal)
        elif button == "C":
            btn = tk.Button(calc_window, text=button, padx=20, pady=20, font=("Arial", 18), bg="red",
                            command=button_clear)
        elif button == "Del":
            btn = tk.Button(calc_window, text=button, padx=20, pady=20, font=("Arial", 18), bg="orange",
                            command=button_remove)
        else:
            btn = tk.Button(calc_window, text=button, padx=20, pady=20, font=("Arial", 18),
                            command=lambda b=button: button_click(b))

        btn.grid(row=row_val, column=col_val, padx=5, pady=5)
        col_val += 1
        if col_val > 3:
            col_val = 0
            row_val += 1


root = tk.Tk()
root.title("Personal Finance Tracker")
root.geometry("800x600")


fullscreen_button = tk.Button(root, text="Toggle Fullscreen", command=toggle_fullscreen, bg="#4CAF50", fg="white")
fullscreen_button.grid(row=0, column=2, pady=10, padx=10)


description_var = tk.StringVar()
amount_var = tk.StringVar()
date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))

tk.Label(root, text="Description:", font=("Arial", 12), bg="#e0f7fa").grid(row=1, column=0, padx=10, pady=5, sticky='e')
tk.Entry(root, textvariable=description_var, font=("Arial", 12), bg="#ffffff").grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Amount:", font=("Arial", 12), bg="#e0f7fa").grid(row=2, column=0, padx=10, pady=5, sticky='e')
tk.Entry(root, textvariable=amount_var, font=("Arial", 12), bg="#ffffff").grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Date (YYYY-MM-DD):", font=("Arial", 12), bg="#e0f7fa").grid(row=3, column=0, padx=10, pady=5, sticky='e')
tk.Entry(root, textvariable=date_var, font=("Arial", 12), bg="#ffffff").grid(row=3, column=1, padx=10, pady=5)

add_button = tk.Button(root, text="Add Transaction", command=add_transaction, bg="#4CAF50", fg="white", font=("Arial", 12))
add_button.grid(row=4, column=1, pady=10, sticky='w')


message_label = tk.Label(root, text="", font=("Arial", 12), fg="green", bg="#f0f0f0")
message_label.grid(row=5, column=0, columnspan=2)


tk.Button(root, text="Show Daily Summary", command=show_daily_summary, bg="#2196F3", fg="white", font=("Arial", 12)).grid(row=6, column=0, padx=10, pady=5, sticky='e')
tk.Button(root, text="Show Monthly Summary", command=show_monthly_summary, bg="#2196F3", fg="white", font=("Arial", 12)).grid(row=6, column=1, padx=10, pady=5, sticky='w')

tk.Button(root, text="List Transactions", command=show_transactions_list, bg="#FFC107", fg="white", font=("Arial", 12)).grid(row=7, column=0, padx=10, pady=5, sticky='e')


tk.Button(root, text="Open Calculator", command=open_calculator, bg="#FF5722", fg="white", font=("Arial", 12)).grid(row=7, column=1, padx=10, pady=5, sticky='w')


root.mainloop()