🏦 ATM Management System (Python + Tkinter + MySQL)

A GUI-based ATM Management System built using Python (Tkinter) and MySQL, simulating real-world ATM functionalities such as cash withdrawal, deposit, balance enquiry, fund transfer, PIN change, and user authentication with OTP verification.

🚀 Features
🔐 User & Account Management

New account registration with:
Mobile number verification (OTP)
Aadhaar validation
Initial deposit
Login & registration using User ID + Password
Forgot credentials with OTP-based recovery

💳 ATM Operations

Cash Deposit
Cash Withdrawal
Fast Cash (₹200, ₹500, ₹1000, ₹5000)
Balance Enquiry
Mini Statement (last 10 transactions)
Fund Transfer (Account to Account)
Change PIN
Update registered mobile number

📜 Transaction Handling

All transactions stored in MySQL
Auto timestamping of transactions
Separate transaction types:
deposit
withdraw
fastcash

transfer_in / transfer_out
⏱ Security & UX
OTP verification using Twilio

ATM-Management-System/
│
├── AtmProjectCode.py     # Main application file
├── README.md             # Project documentation

⚙️ Installation & Setup
1️⃣ Prerequisites
Python 3.8+
MySQL Server
Twilio Account (for OTP)

2️⃣ Install Required Packages
pip install pymysql twilio

3️⃣ Configure MySQL
Create a database named:
CREATE DATABASE atm;
Update MySQL credentials in code if needed:
connect(host="localhost", user="root", password="", db="atm")

4️⃣ Configure Twilio
Replace in send_otp():
account_sid = 'Your_Id'
auth_token = 'Your_Token'
from_ = '+Your_Twilio_Number'


▶️ How to Run
python AtmProjectCode.py

The database tables will be created automatically on first run.

📸 Screens Included
Login / Registration Screen
ATM Dashboard
Deposit / Withdraw / Fast Cash
OTP Verification
Transaction History



⚠️ Important Notes
Aadhaar validation API is mocked
Passwords & PINs are stored in plain text (not production-ready)
Intended for academic / learning purposes only



📌 Future Improvements
Password hashing (bcrypt)
Role-based access
REST API backend
Cloud database support
Enhanced UI design


👩‍💻 Author
Karishma Srivastava
