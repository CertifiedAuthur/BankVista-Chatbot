import db_helper
from session_manager import active_sessions
import asyncio


# session_id = generic_helper.extract_session_id(output_contexts)
    
# Function to initiate the transaction using MockTransaction
def process_transaction(user_data, session_id, session_dict):
    session_data = db_helper.get_session(session_id)
    if session_data:
        username = session_data[1]
    if username:
        # Use the stored username
        account_id = db_helper.is_user_registered(username)
    else:
        # Handle the case where username is not found in the session
        print("Username not found in session")
    account_id = db_helper.is_user_registered(username)
    
    print(account_id)  # Debugging line

    # Retrieve transaction details from user_data
    amount = user_data.get('amount')
    beneficiary_name = user_data.get('account_name')

    # Convert 'account_numbers' list to a comma-separated string    
    beneficiary_account_number = user_data.get('account_number')
    if isinstance(beneficiary_account_number, list):
        beneficiary_account_number = beneficiary_account_number[0]
    beneficiary_bank = user_data.get('bank_name')

    # Add logic to handle transaction processing using these variables
    # For example, constructing and executing a SQL query


    # Create the mock transaction
    transaction = db_helper.MockTransaction(
        account_id=account_id,
        amount=amount,
        beneficiary_name=beneficiary_name,
        beneficiary_account_number=beneficiary_account_number,
        beneficiary_bank=beneficiary_bank
    )
    
    


    # Initiate the transaction and get the insert query
    insert_query, insert_params = transaction.initiate_transaction()
    
    print(f"Transaction completed successfully. Transaction ID: {transaction.transaction_id}, Amount: {transaction.amount} to {beneficiary_name} at {beneficiary_bank}.")

    # Execute the query to insert the transaction details into the database
    asyncio.create_task(execute_transaction([insert_query], [insert_params]))  # Use your execute_queries function here

    # Simulate completing the transaction and get the update query
    update_query, update_params = transaction.complete_transaction()

    # Execute the query to update the transaction status
    asyncio.create_task(execute_transaction([update_query], [update_params]))

    # Return the response message based on the transaction status
    return f"Transaction completed successfully. Transaction ID: {transaction.transaction_id}, Amount: {transaction.amount} to {beneficiary_name} at {beneficiary_bank}."

async def execute_transaction(queries, params):
    # Execute the query asynchronously
    try:
        # Execute the query asynchronously
        await db_helper.execute_queries(queries, params)
    except Exception as e:
        print(f"Error executing query: {e}")