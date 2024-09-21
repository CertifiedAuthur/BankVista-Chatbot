-- Step 1: Create the BankVista database
CREATE DATABASE IF NOT EXISTS BankVistaDB;

-- Step 2: Use the BankVista database
USE BankVistaDB;

-- Step 3: Create the accounts table with a 12-digit account ID
CREATE TABLE accounts (
    account_id CHAR(12) PRIMARY KEY,  -- Account ID is 12 characters long with only digits
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_holder_name VARCHAR(100) NOT NULL,
    account_type ENUM('savings', 'current') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 4: Create the transactions table with updated schema including transaction_date
CREATE TABLE transactions (
    transaction_id CHAR(12) PRIMARY KEY,  -- Transaction ID is 12 characters long with mixed digits and characters
    account_id CHAR(12),
    transaction_type ENUM('deposit', 'withdrawal', 'transfer') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- Date and time of the transaction
    status ENUM('successful', 'pending', 'failed') NOT NULL,  -- Transaction status
    beneficiary_name VARCHAR(100),  -- Name of the beneficiary
    beneficiary_account_number VARCHAR(20),  -- Account number of the beneficiary
    beneficiary_bank VARCHAR(100),  -- Bank of the beneficiary
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Step 5: Create the authentication table
CREATE TABLE authentication (
    auth_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id CHAR(12),
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

-- Step 6: Create the account_status table
CREATE TABLE account_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id CHAR(12),
    status ENUM('active', 'inactive') NOT NULL,
    status_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE news (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    importance ENUM('high', 'mild', 'low') NOT NULL DEFAULT 'low',
    date DATE NOT NULL,
    category VARCHAR(50),
    tags VARCHAR(255)
);

-- Step 7: Insert sample data into accounts
INSERT INTO accounts (account_id, account_number, account_holder_name, account_type) VALUES
('123456789012', 'ACC123456', 'John Doe', 'savings'),
('234567890123', 'ACC654321', 'Jane Smith', 'current'),
('345678901234', 'ACC789012', 'Bob Johnson', 'savings'); 

-- Step 8: Insert sample data into transactions
INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, transaction_date, status, beneficiary_name, beneficiary_account_number, beneficiary_bank) VALUES
('TX123456789A', '123456789012', 'deposit', 500.00, '2024-08-29 10:00:00', 'successful', 'Alice Brown', 'BEN123456', 'Bank A'),
('TX234567890B', '234567890123', 'withdrawal', 200.00, '2024-08-28 15:30:00', 'pending', 'Bob Green', 'BEN654321', 'Bank B'),
('TX345678901C', '345678901234', 'deposit', 1000.00, '2024-08-27 09:45:00', 'failed', 'Charlie Black', 'BEN789012', 'Bank C');

-- Step 9: Insert sample data into account_status
INSERT INTO account_status (account_id, status) VALUES
('123456789012', 'active'),
('234567890123', 'inactive'),
('345678901234', 'active');

-- Step 10: Insert sample data into authentication
INSERT INTO authentication (account_id, username, password_hash) VALUES
('123456789012', 'johndoe', 'hashed_password_1'), -- Replace 'hashed_password_1' with an actual hashed password
('234567890123', 'janesmith', 'hashed_password_2'), -- Replace 'hashed_password_2' with an actual hashed password
('345678901234', 'bobjohnson', 'hashed_password_3'); -- Replace 'hashed_password_3' with an actual hashed password

-- Step 11: Insert news into news
INSERT INTO news (title, content, importance, date, category, tags)
VALUES 
('Company Achieves Record Profits', 'BankVista has reported record profits in Q3, exceeding market expectations.', 'high', '2024-09-01', 'Finance', 'profits, financial results'),
('New Financial Regulations Announced', 'New regulations affecting the financial sector will come into effect next quarter.', 'mild', '2024-08-20', 'Finance', 'regulations, financial sector'), 
('New Branch Opening', 'We are excited to announce the opening of a new branch in Downtown.', 'mild', '2024-08-15', 'Company', 'branch, expansion'),
('Employee of the Month Awards', 'Congratulations to Jane Doe for being named Employee of the Month for August.', 'low', '2024-08-10', 'Company', 'awards, employee recognition'),
('Launch of New Mobile App', 'BankVista has launched a new mobile app to enhance customer experience.', 'high', '2024-09-05', 'Technology', 'app launch, mobile');


-- Step 11: Create the get_account_balance function
DELIMITER $$

CREATE FUNCTION get_account_balance(p_account_id CHAR(12)) RETURNS DECIMAL(10,2)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_balance DECIMAL(10,2);
    
    SELECT 
        IFNULL(SUM(CASE WHEN transaction_type = 'deposit' THEN amount ELSE 0 END), 0) -
        IFNULL(SUM(CASE WHEN transaction_type = 'withdrawal' THEN amount ELSE 0 END), 0)
    INTO v_balance
    FROM transactions
    WHERE account_id = p_account_id;
    
    RETURN v_balance;
END$$

DELIMITER ;

-- Step 12: Test the get_account_balance function (Optional)
SELECT get_account_balance('123456789012') AS 'Account 1 Balance';
SELECT get_account_balance('234567890123') AS 'Account 2 Balance';
SELECT get_account_balance('345678901234') AS 'Account 3 Balance';
