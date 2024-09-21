import re
import spacy

def extract_session_id(contexts):
    for context in contexts:
        context_name = context.get('name', '')
        match = re.search(r"/sessions/(.*?)/contexts/", context_name)
        if match:
            return match.group(1)
    return None

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

import re

def extract_name_from_text(text):
    print(f"Input text: {text}")
    
    # Simple rule-based approach
    name_pattern = r"(my name is|my name's|i'm) (.+)"
    match = re.search(name_pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(2).strip()
    
    # Handle cases where user simply enters their name
    name_pattern = r"^\s*(.+)\s*$"
    match = re.search(name_pattern, text, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None


# Define custom component for extracting username and password
def extract_credentials(text):
    # Patterns for different phrases
    username_patterns = [
        r'\busername\s+is\s+(\S+)\b',
        r'\buser\s+name\s*:\s*(\S+)\b',
        r'\bmy\s+username\s+is\s+(\S+)\b',
        r'\bi\s+am\s+(\S+)\b',
        r'\buser\s+(\S+)\b'
    ]

    password_patterns = [
        r'\bpassword\s+is\s+(\S+)\b',
        r'\bpass\s*:\s*(\S+)\b',
        r'\bmy\s+password\s+is\s+(\S+)\b',
        r'\bpassword\s+(\S+)\b'
    ]

    username = None
    password = None

    # Try matching all patterns
    for pattern in username_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            username = match.group(1)
            break

    for pattern in password_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            password = match.group(1)
            break

    return username, password

def extract_account_numbers(query_text):
    # Define a regex pattern for exactly 10-digit account numbers
    pattern = r'\b\d{10}\b'

    # Find all matches in the text
    account_numbers = re.findall(pattern, query_text)

    return account_numbers


def extract_account_name(query_text):
    # Define a pattern to capture the account name after the words 'account name'
    pattern = r'(?i)(account name is|account name:|account name)\s*([A-Za-z\s]+)'

    # Search for the account name pattern in the text
    match = re.search(pattern, query_text)

    # If a match is found, extract the name group
    if match:
        account_name = match.group(2).strip()
        return account_name
    else:
        return None
    
    
def extract_username(sentence):
    # Define possible patterns for extracting the username
    patterns = [
        r'username\s*is\s*(\w+)',           # "username is janesmith"
        r'my\s*username\s*is\s*(\w+)',       # "my username is janesmith"
        r'username\s*:\s*(\w+)',             # "username: janesmith"
        r'(\w+)\s*is\s*my\s*username',       # "janesmith is my username"
        r'username\s*=\s*(\w+)'              # "username = janesmith"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None  # If no match is found


