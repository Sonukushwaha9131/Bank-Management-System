import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime

# ==========================
# FILES
# ==========================

DATA_FILE = "data.json"
TRANSACTION_FILE = "transactions.json"


# ==========================
# JSON LOADERS
# ==========================

def load_json(filename):
    try:
        if Path(filename).exists():
            with open(filename, "r") as f:
                content = f.read().strip()

                if not content:
                    return []

                return json.loads(content)

    except Exception:
        return []

    return []


users = load_json(DATA_FILE)
transactions = load_json(TRANSACTION_FILE)


# ==========================
# SAVE FUNCTIONS
# ==========================

def save_users():
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


def save_transactions():
    with open(TRANSACTION_FILE, "w") as f:
        json.dump(transactions, f, indent=4)


# ==========================
# ACCOUNT GENERATOR
# ==========================

def generate_account_number():

    while True:

        account = ''.join(
            random.choices(
                string.ascii_uppercase +
                string.digits,
                k=10
            )
        )

        exists = any(
            user["account_no"] == account
            for user in users
        )

        if not exists:
            return account


# ==========================
# STREAMLIT PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="Bank Management System",
    page_icon="🏦",
    layout="wide"
)

st.title("🏦 Bank Management System")


# ==========================
# SESSION
# ==========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


# ==========================
# SIDEBAR MENU
# ==========================

if not st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Select Option",
        [
            "Create Account",
            "Login"
        ]
    )

    # ==========================
    # CREATE ACCOUNT
    # ==========================

    if menu == "Create Account":

        st.subheader("Create New Account")

        name = st.text_input("Full Name")

        age = st.number_input(
            "Age",
            min_value=1,
            max_value=100,
            step=1
        )

        email = st.text_input("Email")

        pin = st.text_input(
            "4 Digit PIN",
            type="password"
        )

        if st.button("Create Account"):

            if age < 18:
                st.error("Age must be at least 18.")

            elif len(pin) != 4 or not pin.isdigit():
                st.error("PIN must be exactly 4 digits.")

            elif any(
                    user["email"] == email
                    for user in users):
                st.error("Email already registered.")

            else:

                account_no = generate_account_number()

                user = {
                    "name": name,
                    "age": age,
                    "email": email,
                    "pin": pin,
                    "account_no": account_no,
                    "balance": 0
                }

                users.append(user)
                save_users()

                st.success(
                    "Account Created Successfully!"
                )

                st.info(
                    f"Your Account Number: {account_no}"
                )

    # ==========================
    # LOGIN
    # ==========================

    elif menu == "Login":

        st.subheader("Login")

        account_no = st.text_input(
            "Account Number"
        )

        pin = st.text_input(
            "PIN",
            type="password"
        )

        if st.button("Login"):

            user = next(
                (
                    u for u in users
                    if u["account_no"] == account_no
                    and u["pin"] == pin
                ),
                None
            )

            if user:

                st.session_state.logged_in = True
                st.session_state.user = user

                st.success("Login Successful")
                st.rerun()

            else:
                st.error("Invalid Credentials")

# ==========================
# DASHBOARD
# ==========================

else:

    user = st.session_state.user

    st.sidebar.success(
        f"Welcome {user['name']}"
    )

    dashboard = st.sidebar.radio(
        "Dashboard",
        [
            "Profile",
            "Deposit",
            "Withdraw",
            "Transactions",
            "Update Profile",
            "Delete Account",
            "Logout"
        ]
    )

    # ==========================
    # PROFILE
    # ==========================

    if dashboard == "Profile":

        st.subheader("Account Details")

        st.write(
            f"### Name: {user['name']}"
        )

        st.write(
            f"### Email: {user['email']}"
        )

        st.write(
            f"### Age: {user['age']}"
        )

        st.write(
            f"### Account Number: {user['account_no']}"
        )

        st.metric(
            "Available Balance",
            f"₹ {user['balance']}"
        )

    # ==========================
    # DEPOSIT
    # ==========================

    elif dashboard == "Deposit":

        st.subheader("Deposit Money")

        amount = st.number_input(
            "Enter Amount",
            min_value=1
        )

        if st.button("Deposit"):

            user["balance"] += amount

            transactions.append({
                "account_no": user["account_no"],
                "type": "Deposit",
                "amount": amount,
                "time": datetime.now().strftime(
                    "%d-%m-%Y %H:%M:%S"
                )
            })

            save_users()
            save_transactions()

            st.success(
                f"₹{amount} Deposited Successfully"
            )

    # ==========================
    # WITHDRAW
    # ==========================

    elif dashboard == "Withdraw":

        st.subheader("Withdraw Money")

        amount = st.number_input(
            "Enter Amount",
            min_value=1
        )

        if st.button("Withdraw"):

            if amount > user["balance"]:

                st.error(
                    "Insufficient Balance"
                )

            else:

                user["balance"] -= amount

                transactions.append({
                    "account_no": user["account_no"],
                    "type": "Withdraw",
                    "amount": amount,
                    "time": datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    )
                })

                save_users()
                save_transactions()

                st.success(
                    f"₹{amount} Withdrawn Successfully"
                )

    # ==========================
    # TRANSACTIONS
    # ==========================

    elif dashboard == "Transactions":

        st.subheader(
            "Transaction History"
        )

        history = [
            t for t in transactions
            if t["account_no"]
            == user["account_no"]
        ]

        if history:
            st.dataframe(history)
        else:
            st.info(
                "No transactions found."
            )

    # ==========================
    # UPDATE PROFILE
    # ==========================

    elif dashboard == "Update Profile":

        st.subheader(
            "Update Profile"
        )

        new_name = st.text_input(
            "Name",
            value=user["name"]
        )

        new_email = st.text_input(
            "Email",
            value=user["email"]
        )

        if st.button(
                "Update Profile"):

            user["name"] = new_name
            user["email"] = new_email

            save_users()

            st.success(
                "Profile Updated Successfully"
            )

    # ==========================
    # DELETE ACCOUNT
    # ==========================

    elif dashboard == "Delete Account":

        st.subheader(
            "Delete Account"
        )

        st.warning(
            "This action cannot be undone."
        )

        confirm = st.checkbox(
            "I understand"
        )

        if confirm:

            if st.button(
                    "Delete My Account"):

                users.remove(user)

                save_users()

                st.session_state.logged_in = False
                st.session_state.user = None

                st.success(
                    "Account Deleted Successfully"
                )

                st.rerun()

    # ==========================
    # LOGOUT
    # ==========================

    elif dashboard == "Logout":

        st.session_state.logged_in = False
        st.session_state.user = None

        st.success("Logged Out")

        st.rerun()