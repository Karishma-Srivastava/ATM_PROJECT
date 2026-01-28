from tkinter import *
from pymysql import connect
from tkinter import messagebox
from datetime import datetime
import random
from twilio.rest import Client
import re  # For Aadhaar format validation


# Initialize the database
def initialize_db():
    try:
        with connect(host="localhost", user="root", password="", db="atm") as conn:
            cursor = conn.cursor()
            # Create necessary tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    account_no VARCHAR(20) PRIMARY KEY,
                    name VARCHAR(50),
                    mobile VARCHAR(15),
                    aadhaar VARCHAR(12),
                    pin VARCHAR(10),
                    balance FLOAT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    account_no VARCHAR(20),
                    type VARCHAR(10),
                    amount FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (account_no) REFERENCES accounts(account_no)
                )
            """)
            conn.commit()
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")

def get_connection():
    try:
        # Establish a connection to the database
        conn = connect(host="localhost", user="root", password="", db="atm")
        return conn
    except Exception as e:
        messagebox.showerror("Database Error", f"Failed to connect to the database: {str(e)}")
        return None

def deposit():
    def process_deposit():
        acc = account_no.get()
        pin_value = pin.get()
        amt_str = amount.get().strip()

        if not amt_str:
            messagebox.showerror("Error", "Amount cannot be empty.")
            return

        try:
            amt = float(amt_str)
            if amt <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND pin = %s", (acc, pin_value))
            result = cursor.fetchone()

            if result:
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_no = %s", (amt, acc))
                cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, 'deposit', %s)", (acc, amt))
                conn.commit()
                messagebox.showinfo("Success", f"₹{amt:.2f} deposited successfully!")
            else:
                messagebox.showerror("Error", "Invalid account number or PIN.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")
        finally:
            conn.close()

    # UI for deposit
    upwin = Toplevel()
    upwin.geometry("380x260")
    upwin.title("Deposit Cash")
    upwin.resizable(0, 0)

    Label(upwin, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(upwin, textvariable=account_no, width=20).place(x=230, y=40)

    Label(upwin, text="Enter PIN", font="Times 15").place(x=26, y=90)
    pin = StringVar()
    Entry(upwin, textvariable=pin, show="*", width=20).place(x=230, y=90)

    Label(upwin, text="Enter amount", font="Times 15").place(x=26, y=140)
    amount = StringVar()
    Entry(upwin, textvariable=amount, width=20).place(x=230, y=140)

    Button(upwin, text="Deposit", font="Times 10", command=process_deposit).place(x=26, y=200)

        # Countdown timer for auto-closing window
    countdown_label = Label(upwin, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=150, y=200)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            upwin.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            upwin.destroy()

    countdown(90)  # Start 90-second countdown

    upwin.mainloop()


def ministate():
    def show_statement():
        acc = account_no.get()
        with connect(host="localhost", user="root", password="", db="atm") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type, amount, timestamp FROM transactions WHERE account_no = %s ORDER BY timestamp DESC LIMIT 10", (acc,))
            transactions = cursor.fetchall()

            if transactions:
                statement_window = Toplevel()
                statement_window.title("Transaction History")
                Label(statement_window, text="Recent Transactions", font="Arial 15 bold").pack()

                for transaction in transactions:
                    Label(statement_window, text=f"Type: {transaction[0]}, Amount: {transaction[1]}, Date: {transaction[2]}").pack()
            else:
                messagebox.showinfo("No Transactions", "No transactions found for this account.")

    upwin = Toplevel()
    upwin.geometry("400x300")
    upwin.title("Mini Statement")
    upwin.resizable(0, 0)

    Label(upwin, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(upwin, textvariable=account_no, width=20).place(x=230, y=40)

    Button(upwin, text="Show", font="Times 10", command=show_statement).place(x=26, y=90)

        # Countdown timer for auto-closing window
    countdown_label = Label(upwin, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=90, y=250)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            upwin.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            upwin.destroy()

    countdown(90)  # Start 90-second countdown

    


def withdraw():
    def process_withdraw():
        acc = account_no.get()
        pin_value = pin.get()
        amt_str = amount.get().strip()

        if not amt_str:
            messagebox.showerror("Error", "Amount cannot be empty.")
            return

        try:
            amt = float(amt_str)
            if amt <= 0:
                messagebox.showerror("Error", "Amount must be greater than 0.")
                return
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid numeric amount.")
            return

        conn = get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND pin = %s", (acc, pin_value))
            result = cursor.fetchone()

            if result:
                current_balance = result[0]
                if current_balance >= amt:
                    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_no = %s", (amt, acc))
                    cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, 'withdraw', %s)", (acc, amt))
                    conn.commit()
                    messagebox.showinfo("Success", f"₹{amt:.2f} withdrawn successfully!")
                else:
                    messagebox.showerror("Error", "Insufficient balance.")
            else:
                messagebox.showerror("Error", "Invalid account number or PIN.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")
        finally:
            conn.close()

    # UI for withdraw
    upwin = Toplevel()
    upwin.geometry("380x260")
    upwin.title("Withdraw Cash")
    upwin.resizable(0, 0)

    Label(upwin, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(upwin, textvariable=account_no, width=20).place(x=230, y=40)

    Label(upwin, text="Enter PIN", font="Times 15").place(x=26, y=90)
    pin = StringVar()
    Entry(upwin, textvariable=pin, show="*", width=20).place(x=230, y=90)

    Label(upwin, text="Enter amount", font="Times 15").place(x=26, y=140)
    amount = StringVar()
    Entry(upwin, textvariable=amount, width=20).place(x=230, y=140)

    Button(upwin, text="Withdraw", font="Times 10", command=process_withdraw).place(x=26, y=200)

        # Countdown timer for auto-closing window
    countdown_label = Label(upwin, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=150, y=200)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            upwin.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            upwin.destroy()

    countdown(90)  # Start 90-second countdown

    upwin.mainloop()

    
def fastcash():
    def quick_withdraw(amount):
        acc = account_no.get()
        pin_value = pin.get()

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND pin = %s", (acc, pin_value))
                result = cursor.fetchone()

                if result and result[0] >= amount:
                    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_no = %s AND pin = %s",
                                   (amount, acc, pin_value))
                    cursor.execute("INSERT INTO transactions (account_no, type, amount) VALUES (%s, 'fastcash', %s)",
                                   (acc, amount))
                    conn.commit()
                    messagebox.showinfo("Success", f"₹{amount} withdrawn successfully!")
                else:
                    messagebox.showerror("Error", "Insufficient balance or invalid credentials.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    # UI for Fast Cash
    win = Toplevel()
    win.geometry("380x280")
    win.title("Fast Cash")
    win.resizable(0, 0)

    Label(win, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(win, textvariable=account_no, width=20).place(x=230, y=40)

    Label(win, text="Enter PIN", font="Times 15").place(x=26, y=90)
    pin = StringVar()
    Entry(win, textvariable=pin, show="*", width=20).place(x=230, y=90)

    Button(win, text="₹200", width=15, command=lambda: quick_withdraw(200)).place(x=20, y=140)
    Button(win, text="₹500", width=15, command=lambda: quick_withdraw(500)).place(x=180, y=140)
    Button(win, text="₹1000", width=15, command=lambda: quick_withdraw(1000)).place(x=20, y=200)
    Button(win, text="₹5000", width=15, command=lambda: quick_withdraw(5000)).place(x=180, y=200)

        # Countdown timer for auto-closing window
    countdown_label = Label(win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=90, y=250)  # Adjusted to fit in the window


    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            win.destroy()

    countdown(90)  # Start 90-second countdown


    

def balenq():
    def check_balance():
        acc = account_no.get()
        pin_value = pin.get()

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND pin = %s", (acc, pin_value))
                result = cursor.fetchone()

                if result:
                    messagebox.showinfo("Balance Enquiry", f"Your current balance is ₹{result[0]:.2f}")
                else:
                    messagebox.showerror("Error", "Invalid account number or PIN.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    # UI for Balance Enquiry
    win = Toplevel()
    win.geometry("400x200")
    win.title("Balance Enquiry")
    win.resizable(0, 0)

    Label(win, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(win, textvariable=account_no, width=20).place(x=250, y=40)

    Label(win, text="Enter PIN", font="Times 15").place(x=26, y=90)
    pin = StringVar()
    Entry(win, textvariable=pin, show="*", width=20).place(x=250, y=90)

    Button(win, text="Check Balance", command=check_balance).place(x=26, y=130)

        # Countdown timer for auto-closing window
    countdown_label = Label(win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=120, y=150)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            win.destroy()

    countdown(90)  # Start 90-second countdown

    win.mainloop()

def pinchange():
    def update_pin():
        acc = account_no.get()
        old_pin = old_pin_var.get()
        new_pin = new_pin_var.get()
        confirm_pin = confirm_pin_var.get()

        if new_pin != confirm_pin:
            messagebox.showerror("Error", "New PIN and confirmation PIN do not match.")
            return

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM accounts WHERE account_no = %s AND pin = %s", (acc, old_pin))
                result = cursor.fetchone()

                if result:
                    cursor.execute("UPDATE accounts SET pin = %s WHERE account_no = %s", (new_pin, acc))
                    conn.commit()
                    messagebox.showinfo("Success", "PIN changed successfully!")
                else:
                    messagebox.showerror("Error", "Invalid account number or old PIN.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    # UI for Change PIN
    win = Toplevel()
    win.geometry("420x300")
    win.title("Change PIN")
    win.resizable(0, 0)

    Label(win, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(win, textvariable=account_no, width=20).place(x=220, y=40)

    Label(win, text="Enter old PIN", font="Times 15").place(x=26, y=90)
    old_pin_var = StringVar()
    Entry(win, textvariable=old_pin_var, show="*", width=20).place(x=220, y=90)

    Label(win, text="Enter new PIN", font="Times 15").place(x=26, y=140)
    new_pin_var = StringVar()
    Entry(win, textvariable=new_pin_var, show="*", width=20).place(x=220, y=140)

    Label(win, text="Confirm new PIN", font="Times 15").place(x=26, y=190)
    confirm_pin_var = StringVar()
    Entry(win, textvariable=confirm_pin_var, show="*", width=20).place(x=220, y=190)

    Button(win, text="Change PIN", command=update_pin).place(x=26, y=240)

        # Countdown timer for auto-closing window
    countdown_label = Label(win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=140, y=250)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            win.destroy()

    countdown(90)  # Start 90-second countdown

    win.mainloop()

def transfer():
    def process_transfer():
        sender_acc = sender_account.get()
        sender_pin = sender_pin_var.get()
        receiver_acc = receiver_account.get()
        amount = float(transfer_amount.get())

        if amount <= 0:
            messagebox.showerror("Error", "Transfer amount must be greater than 0.")
            return

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()

                # Verify sender credentials and balance
                cursor.execute("SELECT balance FROM accounts WHERE account_no = %s AND pin = %s", (sender_acc, sender_pin))
                sender_data = cursor.fetchone()

                if not sender_data:
                    messagebox.showerror("Error", "Invalid sender account or PIN.")
                    return

                sender_balance = sender_data[0]
                if sender_balance < amount:
                    messagebox.showerror("Error", "Insufficient balance.")
                    return

                # Verify receiver account exists
                cursor.execute("SELECT balance FROM accounts WHERE account_no = %s", (receiver_acc,))
                receiver_data = cursor.fetchone()

                if not receiver_data:
                    messagebox.showerror("Error", "Receiver account does not exist.")
                    return

                # Perform the transfer
                cursor.execute("UPDATE accounts SET balance = balance - %s WHERE account_no = %s", (amount, sender_acc))
                cursor.execute("UPDATE accounts SET balance = balance + %s WHERE account_no = %s", (amount, receiver_acc))

                # Log the transactions
                cursor.execute(
                    "INSERT INTO transactions (account_no, type, amount) VALUES (%s, 'transfer_out', %s)",
                    (sender_acc, amount)
                )
                cursor.execute(
                    "INSERT INTO transactions (account_no, type, amount) VALUES (%s, 'transfer_in', %s)",
                    (receiver_acc, amount)
                )

                conn.commit()
                messagebox.showinfo("Success", f"₹{amount:.2f} transferred successfully!")

        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    # UI for Transfer Funds
    win = Toplevel()
    win.geometry("500x400")
    win.title("Transfer Funds")
    win.resizable(0, 0)

    Label(win, text="Sender Account Number", font="Times 15").place(x=26, y=40)
    sender_account = StringVar()
    Entry(win, textvariable=sender_account, width=20).place(x=280, y=40)

    Label(win, text="Sender PIN", font="Times 15").place(x=26, y=90)
    sender_pin_var = StringVar()
    Entry(win, textvariable=sender_pin_var, show="*", width=20).place(x=280, y=90)

    Label(win, text="Receiver Account Number", font="Times 15").place(x=26, y=140)
    receiver_account = StringVar()
    Entry(win, textvariable=receiver_account, width=20).place(x=280, y=140)

    Label(win, text="Transfer Amount (₹)", font="Times 15").place(x=26, y=190)
    transfer_amount = StringVar()
    Entry(win, textvariable=transfer_amount, width=20).place(x=280, y=190)

    Button(win, text="Transfer", command=process_transfer, font="Times 12").place(x=200, y=250)

        # Countdown timer for auto-closing window
    countdown_label = Label(win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=90, y=300)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            win.destroy()

    countdown(90)  # Start 90-second countdown

    win.mainloop()

def conchange():
    def update_contact():
        acc = account_no.get()
        pin_value = pin.get()
        old_contact = old_contact_var.get()
        new_contact = new_contact_var.get()
        confirm_contact = confirm_contact_var.get()

        if new_contact != confirm_contact:
            messagebox.showerror("Error", "New contact number and confirmation do not match.")
            return

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM accounts WHERE account_no = %s AND pin = %s AND mobile = %s",
                               (acc, pin_value, old_contact))
                result = cursor.fetchone()

                if result:
                    cursor.execute("UPDATE accounts SET mobile = %s WHERE account_no = %s", (new_contact, acc))
                    conn.commit()
                    messagebox.showinfo("Success", "Contact number updated successfully!")
                else:
                    messagebox.showerror("Error", "Invalid account details or old contact number.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    # UI for Change Contact
    win = Toplevel()
    win.geometry("500x340")
    win.title("Update Contact Details")
    win.resizable(0, 0)

    Label(win, text="Enter account number", font="Times 15").place(x=26, y=40)
    account_no = StringVar()
    Entry(win, textvariable=account_no, width=20).place(x=280, y=40)

    Label(win, text="Enter PIN", font="Times 15").place(x=26, y=90)
    pin = StringVar()
    Entry(win, textvariable=pin, show="*", width=20).place(x=280, y=90)

    Label(win, text="Enter old contact number", font="Times 15").place(x=26, y=140)
    old_contact_var = StringVar()
    Entry(win, textvariable=old_contact_var, width=20).place(x=280, y=140)

    Label(win, text="Enter new contact number", font="Times 15").place(x=26, y=190)
    new_contact_var = StringVar()
    Entry(win, textvariable=new_contact_var, width=20).place(x=280, y=190)

    Label(win, text="Confirm new contact", font="Times 15").place(x=26, y=240)
    confirm_contact_var = StringVar()
    Entry(win, textvariable=confirm_contact_var, width=20).place(x=280, y=240)

    Button(win, text="Update Contact", command=update_contact).place(x=26, y=290)

        # Countdown timer for auto-closing window
    countdown_label = Label(win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=180, y=300)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            win.destroy()

    countdown(90)  # Start 90-second countdown

    win.mainloop()

    

# Home page
def front(account_no):
    front_win = Toplevel()
    front_win.geometry("500x330")
    front_win.config(bg="lime")
    front_win.title(f"Welcome {account_no} to PNB ATM")

    Label(front_win, text=f"Account: {account_no}", font="Arial 12 bold", bg="lime").place(x=10, y=10)

    Button(front_win, text="Deposit Cash", width=15, font="Times 15", relief=RAISED, bd=10,command=deposit).place(x=15, y=50)
    Button(front_win, text="Mini Statement", width=15, font="Times 15", relief=RAISED, bd=10,command=ministate).place(x=260, y=50)
    Button(front_win, text="Withdraw Cash", width=15, font="Times 15", relief=RAISED, bd=10,command=withdraw).place(x=15, y=120)
    Button(front_win, text="Fast Cash", width=15, font="Times 15", relief=RAISED, bd=10,command=fastcash).place(x=260, y=120)
    Button(front_win, text="Balance Enquiry", width=15, font="Times 15", relief=RAISED, bd=10,command=balenq).place(x=15, y=190)
    Button(front_win, text="Change PIN", width=15, font="Times 15", relief=RAISED, bd=10,command=pinchange).place(x=260, y=190)
    Button(front_win, text="Transfer Funds", width=15, font="Times 15", relief=RAISED, bd=10,command=transfer).place(x=15, y=260)
    Button(front_win, text="Update Contact", width=15, font="Times 15", relief=RAISED, bd=10,command=conchange).place(x=260, y=260)


    front_win.mainloop()

  


# Validate Account and Prompt for ID/Password
def validate_account(account_no):
    try:
        with connect(host="localhost", user="root", password="", db="atm") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE account_no = %s", (account_no,))
            account = cursor.fetchone()

            if account:
                # If account exists, prompt for ID and password
                login_or_register(account_no)

            if not account_no.strip():
               messagebox.showerror("Error", "Account number cannot be empty!")
               return

            if not account_no.isdigit():
               messagebox.showerror("Error", "Invalid account number! It must contain only numeric characters.")
               return
            
            else:
                messagebox.showerror("Error", "Account not found. Please register as a new user.")
    except Exception as e:
        messagebox.showerror("Database Error", f"Error: {str(e)}")


# ID and Password Setup/Login
# ID and Password Setup/Login
def login_or_register(account_no):
    """Login or Register new user."""
    lr_win = Toplevel()
    lr_win.geometry("400x350")
    lr_win.config(bg="plum")
    lr_win.title("Login or Register")

    Label(lr_win, text="Enter User ID", width=20).place(x=20, y=30)
    user_id_var = StringVar()
    Entry(lr_win, textvariable=user_id_var).place(x=180, y=30)

    Label(lr_win, text="Enter Password", width=20).place(x=20, y=90)
    password_var = StringVar()
    Entry(lr_win, textvariable=password_var, show='*').place(x=180, y=90)

    def register():
        """Validate the account number before allowing registration."""
        user_id = user_id_var.get()
        password = password_var.get()

        if not user_id or not password:
            messagebox.showerror("Input Error", "Both User ID and Password are required!")
            return

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()

                # Check if account exists
                cursor.execute("SELECT mobile FROM accounts WHERE account_no = %s", (account_no,))
                account = cursor.fetchone()

                if not account:
                    messagebox.showerror("Error", "Invalid Account Number! Please contact the bank.")
                    return

                # Check if user already exists for this account number
                cursor.execute("SELECT * FROM users WHERE account_no = %s", (account_no,))
                existing_user = cursor.fetchone()

                if existing_user:
                    messagebox.showerror("Error", "An account already exists for this Account Number. Please login.")
                    return

                # Check if user_id already exists
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                existing_user_id = cursor.fetchone()

                if existing_user_id:
                    messagebox.showerror("Error", "The User ID already exists. Please choose a different User ID.")
                    return

                # Send OTP for verification
                mobile = account[0]
                otp = send_otp(mobile)
                if not otp:
                    return  # Failed to send OTP

                # Prompt for OTP verification
                otp_win = Toplevel()
                otp_win.geometry("300x200")
                otp_win.title("Verify OTP")

                Label(otp_win, text="Enter OTP sent to your mobile").pack(pady=10)
                otp_var = StringVar()
                Entry(otp_win, textvariable=otp_var).pack(pady=5)

                def verify_otp_and_register():
                    entered_otp = otp_var.get()
                    if not entered_otp:
                        messagebox.showerror("Error", "Please enter the OTP.")
                        return

                    if int(entered_otp) == otp:
                        try:
                            with connect(host="localhost", user="root", password="", db="atm") as conn:
                                cursor = conn.cursor()
                                cursor.execute(
                                    "INSERT INTO users (account_no, user_id, password) VALUES (%s, %s, %s)",
                                    (account_no, user_id, password),
                                )
                                conn.commit()
                                messagebox.showinfo("Success", "User  ID and password set successfully!")
                                otp_win.destroy()
                                lr_win.destroy()
                                front(account_no)  # Proceed to the main ATM menu
                        except Exception as e:
                            messagebox.showerror("Database Error", f"Error: {str(e)}")
                            print(f"Error occurred: {e}")  # Log the error for debugging
                    else:
                        messagebox.showerror("Error", "Invalid OTP. Please try again.")
                

                Button(otp_win, text="Verify OTP", command=verify_otp_and_register).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    def login():
        """Handle login process."""
        user_id = user_id_var.get()
        password = password_var.get()

        if not user_id or not password:
            messagebox.showerror("Input Error", "Both User ID and Password are required!")
            return

        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM users WHERE account_no = %s AND user_id = %s AND password = %s",
                    (account_no, user_id, password),
                )
                user = cursor.fetchone()

                if user:
                    messagebox.showinfo("Success", "Login Successful!")
                    lr_win.destroy()
                    front(account_no)  # Proceed to the main ATM menu
                else:
                    messagebox.showerror("Login Error", "Invalid User ID or Password!")
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    def forgot_credentials():
        """Handle forgotten credentials."""
        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()

                # Check if account number exists
                cursor.execute("SELECT mobile FROM accounts WHERE account_no = %s", (account_no,))
                account = cursor.fetchone()

                if not account:
                    messagebox.showerror("Error", "Invalid Account Number!")
                    return

                # Send OTP for verification
                mobile = account[0]
                otp = send_otp(mobile)
                if not otp:
                    return

                otp_win = Toplevel()
                otp_win.geometry("300x200")
                otp_win.title("Verify OTP")

                Label(otp_win, text="Enter OTP sent to your mobile").pack(pady=10)
                otp_var = StringVar()
                Entry(otp_win, textvariable=otp_var).pack(pady=5)

                def verify_otp():
                    entered_otp = otp_var.get()
                    if not entered_otp:
                        messagebox.showerror("Error", "Please enter the OTP.")
                        return

                    try:
                        # Check if entered OTP is correct
                        if int(entered_otp) == otp:
                            # Proceed to reset credentials
                            otp_win.destroy()
                            
                            # Window for updating credentials
                            reset_win = Toplevel()
                            reset_win.geometry("400x300")
                            reset_win.title("Reset Credentials")

                            Label(reset_win, text="Enter New User ID", width=20).place(x=20, y=30)
                            new_user_id_var = StringVar()
                            Entry(reset_win, textvariable=new_user_id_var).place(x=180, y=30)

                            Label(reset_win, text="Enter New Password", width=20).place(x=20, y=90)
                            new_password_var = StringVar()
                            Entry(reset_win, textvariable=new_password_var, show="*").place(x=180, y=90)

                            def save_new_credentials():
                                new_user_id = new_user_id_var.get()
                                new_password = new_password_var.get()

                                if not new_user_id or not new_password:
                                    messagebox.showerror("Error", "Both fields are required.")
                                    return

                                try:
                                    with connect(host="localhost", user="root", password="", db="atm") as conn:
                                        cursor = conn.cursor()
                                        cursor.execute(
                                            "UPDATE users SET user_id = %s, password = %s WHERE account_no = %s",
                                            (new_user_id, new_password, account_no),
                                        )
                                        conn.commit()
                                        messagebox.showinfo(
                                            "Success", "Credentials updated successfully!"
                                        )
                                        reset_win.destroy()
                                    lr_win.destroy()  # Close the main window after success
                                except Exception as e:
                                    messagebox.showerror("Error", f"An error occurred: {str(e)}")

                            Button(reset_win, text="Save", command=save_new_credentials).place(
                                x=150, y=150
                            )
                        else:
                            messagebox.showerror("Error", "Invalid OTP.")
                    except ValueError:
                        messagebox.showerror("Error", "Invalid OTP format.")
                    except Exception as e:
                        messagebox.showerror("Error", f"An error occurred: {str(e)}")

                Button(otp_win, text="Verify OTP", command=verify_otp).pack(pady=10)

        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    Button(lr_win, text="Login", command=login).place(x=70, y=150)
    Button(lr_win, text="Register", command=register).place(x=200, y=150)
    Button(lr_win, text="Forgot Credentials", command=forgot_credentials).place(x=120, y=200)

        # Countdown timer for auto-closing window
    countdown_label = Label(lr_win, text="Time remaining: 90 seconds",font="Times 12", bg="grey")
    countdown_label.place(x=70, y=250)

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            lr_win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            lr_win.destroy()

    countdown(90)  # Start 90-second countdown


    lr_win.mainloop()
        # Function to send OTP
def send_otp(mobile):
    otp = random.randint(100000, 999999)  # Generate a 6-digit OTP
    try:
                # Twilio Account SID and Auth Token
        account_sid = 'Your_Id'
        auth_token = 'Your_Token'

        client = Client(account_sid, auth_token)
        message = client.messages.create(
        body=f"Your OTP is: {otp}",
        from_='+19789042202',  # Twilio phone number
        to=f'+91{mobile}'  # Replace '+91' with the appropriate country code
    )
        print(f"OTP sent: {message.sid}")
        return otp  # Return the OTP for verification
    except Exception as e:
        print(f"Error sending OTP: {str(e)}")
        messagebox.showerror("Error", f"Failed to send OTP: {str(e)}")
        return None




def validate_aadhaar_api(aadhaar):
    # Mock API validation function
    return True

def new_user():
    reg_win = Toplevel()
    reg_win.geometry("550x480")
    reg_win.config(bg="plum")
    reg_win.title("New User Registration")

    Label(reg_win, text="Name").place(x=30, y=20)
    name = StringVar()
    Entry(reg_win, textvariable=name).place(x=150, y=20)

    Label(reg_win, text="Mobile No").place(x=30, y=60)
    mobile = StringVar()
    Entry(reg_win, textvariable=mobile).place(x=150, y=60)

    otp = None  # To store OTP for verification

    def send_verification():
        nonlocal otp
        otp = send_otp(mobile.get())  # Send OTP to the entered mobile number
        if otp:
            messagebox.showinfo("OTP Sent", "OTP has been sent to your mobile number.")

    Button(reg_win, text="Send OTP", command=send_verification).place(x=370, y=57)

    def verify_otp():
        entered_otp = otp_input.get()
        if otp and entered_otp == str(otp):
            messagebox.showinfo("Success", "OTP verified successfully!")
            register_btn["state"] = NORMAL  # Enable the Register button after OTP verification
        else:
            messagebox.showerror("Error", "Invalid OTP. Please try again.")

    Label(reg_win, text="Aadhaar No").place(x=30, y=100)
    aadhaar = StringVar()
    Entry(reg_win, textvariable=aadhaar).place(x=150, y=100)

    def validate_aadhaar():
        aadhaar_no = aadhaar.get()
        if re.match(r"^\d{12}$", aadhaar_no):  # Check if Aadhaar is 12 digits
            if validate_aadhaar_api(aadhaar_no):
                messagebox.showinfo("Validation", "Aadhaar number validated successfully!")
            else:
                messagebox.showerror("Error", "Aadhaar validation failed. Please enter a valid number.")
        else:
            messagebox.showerror("Error", "Invalid Aadhaar format. Please enter a 12-digit numeric value.")

    Button(reg_win, text="Validate Aadhaar", command=validate_aadhaar).place(x=370, y=97)

    Label(reg_win, text="Set Account No").place(x=30, y=140)
    account_no = StringVar()
    Entry(reg_win, textvariable=account_no).place(x=150, y=140)

    Label(reg_win, text="Set PIN").place(x=30, y=180)
    pin = StringVar()
    Entry(reg_win, textvariable=pin, show='*').place(x=150, y=180)

    Label(reg_win, text="Initial Deposit").place(x=30, y=220)
    deposit = StringVar()
    Entry(reg_win, textvariable=deposit).place(x=150, y=220)

    Label(reg_win, text="Enter OTP").place(x=30, y=260)
    otp_input = StringVar()
    Entry(reg_win, textvariable=otp_input).place(x=150, y=260)

    Button(reg_win, text="Verify OTP", command=verify_otp).place(x=370, y=257)

    def register_account():
        try:
            with connect(host="localhost", user="root", password="", db="atm") as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO accounts (account_no, name, mobile, aadhaar, pin, balance) "
                               "VALUES (%s, %s, %s, %s, %s, %s)",
                               (account_no.get(), name.get(), mobile.get(), aadhaar.get(), pin.get(), deposit.get()))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                reg_win.destroy()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error: {str(e)}")

    register_btn = Button(reg_win, text="Register", command=register_account, state=DISABLED)
    register_btn.place(x=200, y=300)

    # Countdown timer for auto-closing window
    countdown_label = Label(reg_win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=90, y=370)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            reg_win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Registration window has expired!")
            reg_win.destroy()

    countdown(240)  # Start 90-second countdown

    reg_win.mainloop()



def main():
    main_win = Tk()
    main_win.geometry("720x410")
    main_win.config(bg="pink")
    main_win.title("PNB ATM")

    Label(main_win, text="WELCOME TO PUNJAB NATIONAL BANK ATM", bg="pink", font=("arial black", 20)).place(x=20, y=40)

    Label(main_win, text="ENTER ACCOUNT NUMBER", bg="pink", font=("arial black", 15)).place(x=20, y=140)
    account_no = StringVar()
    Entry(main_win, textvariable=account_no, width=20, font=("arial black", 15), bg="wheat").place(x=390, y=140)

    # Submit button for validating account
    Button(main_win, text="Submit", width=10, bg="silver", relief="groove", bd=6, font=("arial black", 10),
           command=lambda: validate_account(account_no.get())).place(x=500, y=180)

    # New user button for opening new account
    Label(main_win, text="If you don't have an account, click the button below.", bg="pink", font=("arial black", 12)).place(x=200, y=270)
    Button(main_win, text="Open New Account", width=17, bg="silver", relief="groove", bd=6, font=("arial black", 10),
           command=new_user).place(x=400, y=310)

    # Countdown timer for auto-closing window
    countdown_label = Label(main_win, text="Time remaining: 90 seconds", font="Times 12", bg="plum")
    countdown_label.place(x=40, y=370)  # Adjusted to fit in the window

    def countdown(time_left):
        if time_left > 0:
            countdown_label.config(text=f"Time remaining: {time_left} seconds")
            main_win.after(1000, countdown, time_left - 1)  # Call again after 1 second
        else:
            messagebox.showinfo("Time's up", "Session expired!")
            main_win.destroy()

    countdown(600)  # Start 90-second countdown

    main_win.mainloop()


# Initialize the database and run the app
initialize_db()
main()
