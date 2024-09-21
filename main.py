import os
import requests
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import generic_helper
from session_manager import active_sessions
import db_helper
import support 
import transactions
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_contexts = payload['queryResult']['outputContexts']
    query_text = payload["queryResult"]["queryText"]
    
    global session_id

    session_id = generic_helper.extract_session_id(output_contexts)
    
    # Mapping intents to their respective handler functions
    intent_handler_dict = {
        'register': handle_registration,
        'register.name': handle_registration_name,
        'register.password': handle_registration_password,
        'register.account-type': handle_registration_account_type,
        'login.auth': handle_login,
        'account.information': handle_account_information,
        'account.balance': handle_account_balance,
        'account.summary': handle_account_summary,
        'recent.transactions': handle_recent_transactions,
        'account.status': handle_account_status,
        'news': handle_news,
        'get.news': get_news,
        'customer.support': handle_rag_query,
        'perform.transactions': handle_payment_flow,
        'account.number': handle_transaction_account_number,
        'account.name': handle_transaction_account_name,
        'amount': handle_transaction_amount,
        'bank': handle_transaction_bank,
        'logout': handle_logout
    }
        
    # Handle the intent
    return intent_handler_dict[intent](parameters, session_id, query_text)

session_dict = {}  # Initialize a session dictionary

def is_valid_name(name):
    if isinstance(name, list):
        return all(item.strip().replace(' ', '').isalpha() for item in name)
    else:
        return name.strip().replace(' ', '').isalpha()

def handle_registration(parameters, session_id, query_text):
    return {"fulfillmentText": "Welcome to the registration process! Please provide your name."}

from session_manager import active_sessions

def handle_registration_name(parameters, session_id, query_text):
    # Check if 'name' is in parameters, if not try to extract it from the query text
    if 'name' in parameters and parameters['name']:
        account_holder_name = parameters['name']
    else:
        # Extract name using the function
        account_holder_name = generic_helper.extract_name_from_text(query_text)

    if account_holder_name:
        active_sessions[session_id] = {'name': account_holder_name}

        if not is_valid_name(account_holder_name):
            return {"fulfillmentText": "Please provide a valid name."}
        else:
            return {"fulfillmentText": "Name received. Please provide a password."}
    else:
        return {"fulfillmentText": "Please provide your name."}


def handle_registration_password(parameters, session_id, query_text):
    if 'password' in parameters:
        password = parameters['password']
        if session_id in active_sessions:
            active_sessions[session_id]['password'] = password
        else:
            active_sessions[session_id] = {'password': password}
        return {"fulfillmentText": "Password received. Please provide your account type (e.g., savings, current)."}
    else:
        return {"fulfillmentText": "Please provide your password."}


def handle_registration_account_type(parameters, session_id, query_text):
    if 'account-type' in parameters:
        account_type = parameters['account-type'].lower()
        if session_id in active_sessions:
            active_sessions[session_id]['account_type'] = account_type
        else:
            active_sessions[session_id] = {'account_type': account_type}

        # Check if 'name' and 'password' exist in active_sessions
        if 'name' in active_sessions[session_id] and 'password' in active_sessions[session_id]:
            # Attempt to register the user
            response_message = db_helper.register_user(account_holder_name=active_sessions[session_id]['name'], password_hash=active_sessions[session_id]['password'], account_type=active_sessions[session_id]['account_type'])

            # Clear session data after registration
            active_sessions.pop(session_id, None)

            return {"fulfillmentText": response_message + " Please log in to access your account."}
        else:
            # Handle the case where 'name' or 'password' is missing
            return {"fulfillmentText": "Please provide your name and password."}
    else:
        return {"fulfillmentText": "Please provide your account type."}

def handle_login(parameters, session_id, query_text):
    # Attempt to extract username and password from the query text first
    username, password = generic_helper.extract_credentials(query_text)
    
    # Print extracted credentials for debugging purposes
    print(f"Extracted Username: {username}")
    print(f"Extracted Password: {password}")

    # If credentials were extracted, use them; otherwise, fall back to parameters
    if username and password:
        try:
            # Attempt to log in with extracted credentials
            db_helper.login_user(session_id, username, password)
            # Store the username in the session dictionary
            db_helper.store_session(session_id, username)
            return {
                "fulfillmentText": (
                    f"Login successful for {username}. Welcome to BankVista! How can we assist you today? "
                    "Options: Account Inquiry, News, Customer Support, Perform Transactions."
                )
            }

        except ValueError:
            # Return an error message if login fails
            return {
                "fulfillmentText": "Invalid username or password. Please try again."
            }
    else:
        # Return a message if credentials could not be extracted or provided
        return {
            "fulfillmentText": "Please provide a valid username and password."
        }

def handle_account_information(parameters, session_id, query_text):
    account_id = active_sessions.get(session_id)
    if account_id:
        account_info = db_helper.get_account_information(account_id)
        return {"fulfillmentText": account_info}
    else:
        return {"fulfillmentText": "Please log in to view your account information."}

def handle_account_balance(parameters, session_id, query_text):
    account_id = active_sessions.get(session_id)
    if account_id:
        balance_info = db_helper.get_account_balance(account_id)
        return {"fulfillmentText": balance_info}
    else:
        return {"fulfillmentText": "Please log in to view your account balance."}

def handle_account_summary(parameters, session_id, query_text):
    account_id = active_sessions.get(session_id)
    if account_id:
        summary_info = db_helper.get_account_summary(account_id)
        return {"fulfillmentText": summary_info}
    else:
        return {"fulfillmentText": "Please log in to view your account summary."}

def handle_recent_transactions(parameters, session_id, query_text):
    account_id = active_sessions.get(session_id)
    if account_id:
        transactions_info = db_helper.get_recent_transactions(account_id)
        return {"fulfillmentText": transactions_info}
    else:
        return {"fulfillmentText": "Please log in to view your recent transactions."}

def handle_account_status(parameters, session_id, query_text):
    account_id = active_sessions.get(session_id)
    if account_id:
        status_info = db_helper.get_account_status(account_id)
        return {"fulfillmentText": status_info}
    else:
        return {"fulfillmentText": "Please log in to view your account status."}
    
def handle_news(parameters, session_id, query_text):
    return {"fulfillmentText": "Please specify the level of importance for the news you wish to read: High, Mild, Low"}

def format_response(news_data):
    response_text = "Here are the latest news updates:"
    for news in news_data:
        response_text += f" {news['title']}"
        response_text += f". {news['content']}"
        response_text += f" Category: {news['category']}"
        response_text += f". Date: {news['date']}"

    response = {
        "fulfillmentText": response_text,
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [response_text]
                }
            }
        ],
        "source": "Here are the latest news updates"
    }
    return response

def get_news(parameters, session_id, query_text):
    # Call the get_news_by_importance function with the specified importance level
    news_data = db_helper.get_news_by_importance(query_text)
    print(news_data)

    # Format the news data into a Dialogflow-compatible response
    response = format_response(news_data)

    return response

def handle_rag_query(parameters, session_id, query_text):
    """
    Function to handle RAG model queries from Dialogflow.
    Calls the chain from support.py to get answers.
    """
    try:
        # Use the RAG model (chain) to get the response based on the query text
        response = support.chain({"question": query_text}, return_only_outputs=True)
        answer = response.get("answer", "Sorry, I couldn't find any relevant information.")
        
        # Return the RAG response as a fulfillment text for Dialogflow
        return {
            "fulfillmentText": answer
        }
    except Exception as e:
        return {
            "fulfillmentText": f"An error occurred while processing your request: {str(e)}"
        }
        
def handle_payment_flow(parameters, session_id, query_text):
    return {"fulfillmentText": "Welcome to the transaction process. Kindly provide the recipient's bank name."}
        
def handle_transaction_bank(parameters, session_id, query_text):
    # Retrieve or initialize user data for the current session
    if session_id not in active_sessions:
        active_sessions[session_id] = {}  # Initialize as a dictionary
    user_data = active_sessions[session_id]

    # Ensure that user_data is a dictionary, not a string
    if not isinstance(user_data, dict):
        active_sessions[session_id] = {}  # Reinitialize if needed
        user_data = active_sessions[session_id]

    # Check if the 'bank' parameter exists and has a value
    if 'bank' in parameters and parameters['bank']:
        bank_name = parameters['bank'][0]
        user_data["bank_name"] = bank_name  # Assign the bank name to the dictionary
        print(user_data)

        return {
            "fulfillmentText": f"Great! You've selected {bank_name}. Please provide the account number."
        }
    else:
        return {
            "fulfillmentText": "Which bank would you like to send money to? Please specify the bank."
        }


def handle_transaction_account_number(parameters, session_id, query_text):
    user_data = active_sessions.get(session_id, {})

    # if 'account_number' in parameters and parameters['account_number']:
    #     account_number = parameters['account_number']
    # else:
    #     # Extract using the function
    account_number = generic_helper.extract_account_numbers(query_text)
        
    if account_number:
        user_data['account_number'] = account_number
        print(user_data)
        active_sessions[session_id] = user_data
        return {"fulfillmentText": "What's the account holder's name?"}
    else:
        return {"fulfillmentText": "Please provide the account number."}


def handle_transaction_account_name(parameters, session_id, query_text):
    user_data = active_sessions.get(session_id, {})

    # if 'account_name' in parameters and parameters['account_name']:
    #     account_name = parameters['account_name']
    # else:
        # Extract using the function
    account_name = generic_helper.extract_account_name(query_text)
        
    if account_name:
        user_data['account_name'] = account_name
        active_sessions[session_id] = user_data
        return {"fulfillmentText": "How much would you like to send?"}
    else:
        return {"fulfillmentText": "Please provide the account holder's name."}

def handle_transaction_amount(parameters, session_id, query_text):
    user_data = active_sessions.get(session_id, {})

    amount = parameters.get('amount', parameters.get('any', ''))
    
    if amount:
        user_data['amount'] = amount
        active_sessions[session_id] = user_data

        # Process the transaction
        response_message = transactions.process_transaction(user_data, session_id, session_dict)

        # Clear session after transaction
        active_sessions.pop(session_id, None)
        return {"fulfillmentText": response_message}
    else:
        return {"fulfillmentText": "How much would you like to send?"}


def handle_logout(parameters, session_id, query_text):
    if db_helper.get_session(session_id):
        db_helper.delete_session(session_id)
        return {"fulfillmentText": "You have been logged out successfully."}
    else:
        return {"fulfillmentText": "You are not currently logged in."}
