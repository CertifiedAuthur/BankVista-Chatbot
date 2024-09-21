from contextlib import contextmanager
import mysql.connector
from session_manager import active_sessions
import uuid
import secrets
import random, string
from datetime import datetime
import transactions

# Establish a global database connection

@contextmanager
def get_connection():
    cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="6877",
        database="bankvistadb"
    )
    try:
        yield cnx
    finally:
        cnx.close()
        
def execute_queries(queries, params):
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            for query, param in zip(queries, params):
                print("Executing query with params:", param)
                cursor.execute(query, param)
            cnx.commit()  # Commit changes only after all queries have been executed
            
async def execute_payment(queries, params):
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            for query, param in zip(queries, params):
                print("Executing query with params:", param)
                cursor.execute(query, param)
            cnx.commit()  # Commit changes only after all queries have been executed
        
def execute_login_query(query, params, fetch=True):
    try:
        with get_connection() as cnx:
            with cnx.cursor(dictionary=True) as cursor:
                params = ensure_list(params)
                print("Executing query with params:", params)
                cursor.execute(query, params)
                if fetch:
                    result = cursor.fetchall()
                    return result
                else:
                    cnx.commit()  # Commit changes if fetch is False
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Handle the error or raise a custom exception

def account_query(query, params, fetch=False):
    with get_connection() as cnx:
        with cnx.cursor(dictionary=True) as cursor:
            params = ensure_list(params)
            params = params[0]
            print("Executing query with params:", params)
            cursor.execute(query, params)
            result = cursor.fetchall()  # Fetch all results to avoid unprocessed results
    return result
            
def ensure_list(params):
    if isinstance(params, list):
        # Flatten the list if it contains sub-lists
        return [item for sublist in params for item in (sublist if isinstance(sublist, list) else [sublist])]
    return [params]


def generate_username(account_holder_name: str) -> str:
    # Remove spaces and lowercase the name
    sanitized_name = account_holder_name.replace(" ", "").lower()
    
    # Generate a unique suffix using UUID
    unique_suffix = str(uuid.uuid4())[:3]
    
    # Combine the name and unique suffix
    username = f"{sanitized_name}{unique_suffix}"
    
    return username

def is_user_registered(username: str) -> bool:
    query = "SELECT account_id FROM authentication WHERE username = %s"
    result = execute_login_query(query, username, fetch=True)
    return result[0]['account_id'] if result else None

def login_user(session_id: str, username: str, password: str) -> None:
    query = "SELECT account_id FROM authentication WHERE username = %s AND password_hash = %s"
    result = execute_login_query(query, [username, password])

    if result:
        active_sessions[session_id] = result[0]['account_id']  # Store account_id in the session
    else:
        raise ValueError("Invalid credentials")

def register_user(account_holder_name: str, password_hash: str, account_type: str) -> str:
    try:
        # Generate username
        username = generate_username(account_holder_name)
        
        # Generate account ID and number (12 and 10 digits, no hyphens)
        account_id = str(random.randint(100000000000, 999999999999))
        account_number = str(random.randint(1000000000, 9999999999))
        status = str("active")
        
        # Hash password
        password_hash = secrets.token_urlsafe(5)
        
        print(f"account_id: {account_id}, type: {type(account_id)}")
        print(f"account_number: {account_number}, type: {type(account_number)}")
        print(f"account_holder_name: {account_holder_name}, type: {type(account_holder_name)}")
        print(f"account_type: {account_type}, type: {type(account_type)}")
        print(f"password_hash: {password_hash}, type: {type(password_hash)}")
        
        
        queries = [
            "INSERT INTO accounts (account_id, account_number, account_holder_name, account_type) VALUES (%s, %s, %s, %s)",
            "INSERT INTO account_status (account_id, status) VALUES (%s, %s)",
            "INSERT INTO authentication (account_id, username, password_hash) VALUES (%s, %s, %s)"
        ]
        
        params = [
        (account_id, account_number, account_holder_name, account_type),
        (account_id, status),
        (account_id, username, password_hash)
        ]
        execute_queries(queries, params)
        
        return f"Registration successful! Your username is {username} and Your password is {password_hash}. Please store your password safely.Welcome aboard! Log in now to access your account and start managing your finances."
    
    except Exception as e:
        return f"Registration failed: {str(e)}"

def get_account_information(account_id: str) -> str:
    query = "SELECT account_number, account_holder_name, account_type FROM accounts WHERE account_id = %s"
    result = account_query(query, (account_id,), fetch=True)
    if result:
        account = result[0]
        return f"Account Number: {account['account_number']}, Account Holder: {account['account_holder_name']}, Account Type: {account['account_type']}"
    else:
        return "Account information not found."

def get_account_balance(account_id: str) -> str:
    query = """
    SELECT
    IFNULL(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END), 0) -
    IFNULL(SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END), 0) AS balance
    FROM transactions
    WHERE account_id = %s
    """
    result = account_query(query, (account_id,), fetch=True)
    balance = result[0]['balance'] if result else 0
    return f"Your current balance for account {account_id} is ${balance:.2f}."

def get_account_summary(account_id: str) -> str:
    query = """
    SELECT
    (SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE account_id = %s AND transaction_type = 'deposit') AS total_deposits,
    (SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE account_id = %s AND transaction_type = 'withdrawal') AS total_withdrawals
    """
    result = account_query(query, (account_id, account_id), fetch=True)
    if result:
        summary = result[0]
        return f"Account Summary: Total Deposits: ${summary['total_deposits']:.2f}, Total Withdrawals: ${summary['total_withdrawals']:.2f}."
    else:
        return "Account summary not found."

def get_recent_transactions(account_id: str) -> str:
    query = "SELECT transaction_id, transaction_type, amount, transaction_date FROM transactions WHERE account_id = %s ORDER BY transaction_date DESC LIMIT 5"
    result = account_query(query, (account_id,), fetch=True)
    transactions = [f"ID: {tx['transaction_id']}, Type: {tx['transaction_type']}, Amount: ${tx['amount']:.2f}, Date: {tx['transaction_date']}" for tx in result]
    return "Recent Transactions:\n" + "\n".join(transactions) if transactions else "No recent transactions found."

def get_account_status(account_id: str) -> str:
    query = "SELECT status FROM account_status WHERE account_id = %s"
    result = account_query(query, (account_id,), fetch=True)
    if result:
        status = result[0]['status']
        return f"The account {account_id} is {status.upper()}."
    else:
        return "Account status not found."
    
def get_news_by_importance(importance: str):
    query = "SELECT title, content, date, category FROM news WHERE importance = %s"
    result = account_query(query, (importance,), fetch=True)
    
    if result:
        return result  # Return the result as a list of dictionaries
    else:
        return []  # Return an empty list if no results
    
class MockTransaction:
    def __init__(self, account_id, amount, beneficiary_name, beneficiary_account_number, beneficiary_bank):
        self.transaction_id = self.generate_transaction_id()
        self.account_id = account_id
        self.transaction_type = 'transfer'
        self.amount = amount
        self.transaction_date = datetime.now()
        self.status = 'pending'  # Initial status
        self.beneficiary_name = beneficiary_name
        self.beneficiary_account_number = beneficiary_account_number
        self.beneficiary_bank = beneficiary_bank

    def generate_transaction_id(self):
        # Generate a 9-digit number followed by 1 uppercase letter
        digits = ''.join(random.choices(string.digits, k=9))  # 9 random digits
        letter = random.choice(string.ascii_uppercase)  # 1 random uppercase letter
        transaction_id = f"TX{digits}{letter}"  # Concatenate TX, digits, and letter
        return transaction_id

    def initiate_transaction(self):
        # Simulate initiating a transaction (sets the status and generates query)
        self.status = "pending"
        print(f"Transaction {self.transaction_id} initiated.")
        return self.generate_transaction_queries()

    def complete_transaction(self):
        # Simulate completing a transaction (sets the status and generates query)
        self.status = "successful"
        print(f"Transaction {self.transaction_id} completed.")
        return self.generate_update_status_query()
    

    def generate_transaction_queries(self):
        # Create a list of queries and parameters for inserting a transaction
        # try:
        insert_transaction_query = """
            INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, 
            transaction_date, status, beneficiary_name, beneficiary_account_number, beneficiary_bank)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        transaction_params = (
            self.transaction_id, self.account_id, self.transaction_type, self.amount,
            self.transaction_date, self.status, self.beneficiary_name,
            self.beneficiary_account_number, self.beneficiary_bank
        )
        
        return insert_transaction_query, transaction_params

    def generate_update_status_query(self):
        # Create a query and parameter set for updating the transaction status
        update_status_query = "UPDATE transactions SET status = %s WHERE transaction_id = %s"
        status_params = (self.status, self.transaction_id)
        
        # Return the query and params for later execution
        return update_status_query, status_params
    
# Function to store session data in the database
def store_session(session_id, user_id):
    try:
        with get_connection() as cnx:
            cursor = cnx.cursor()
            query = "INSERT INTO sessions (session_id, user_id) VALUES (%s, %s)"
            cursor.execute(query, (session_id, user_id))
            cnx.commit()
            cursor.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        # Handle the error or raise a custom exception

# Function to retrieve session data from the database
def get_session(session_id):
    query = "SELECT * FROM sessions WHERE session_id = %s"
    with get_connection() as cnx:
        cursor = cnx.cursor()
        cursor.execute(query, (session_id,))
        return cursor.fetchone()

# Function to delete session data from the database
def delete_session(session_id):
    query = "DELETE FROM sessions WHERE session_id = %s"
    with get_connection() as cnx:
        cursor = cnx.cursor()
        cursor.execute(query, (session_id,))
        cnx.commit()


    


