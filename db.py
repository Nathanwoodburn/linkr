import mysql.connector
import os
import dotenv
import json
import time

dotenv.load_dotenv()

# Database connection
dbargs = {
    'host':os.getenv('DB_HOST'),
    'user':os.getenv('DB_USER'),
    'password':os.getenv('DB_PASSWORD'),
    'database':os.getenv('DB_NAME')
}

last_check_link = 0
links = 0
last_check_account = 0
accounts = 0

def check_tables():
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS links (
            id INT(11) NOT NULL AUTO_INCREMENT,
            owner VARCHAR(255) NOT NULL,
            url VARCHAR(255) NOT NULL,
            link MEDIUMTEXT NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tokens (
            id INT(11) NOT NULL AUTO_INCREMENT,
            token VARCHAR(255) NOT NULL,
            owner VARCHAR(255) NOT NULL,
            PRIMARY KEY (id)
        )
    """)
    cursor.close()
    connection.close()
    print("Checked tables")

def get_link_count():
    global last_check_link
    if time.time() - last_check_link < 60:
        return links

    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM links")
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    last_check_link = time.time()
    if result == None:
        return 0
    
    return result[0]

def get_account_count():
    global last_check_account
    global accounts
    if time.time() - last_check_account < 60:
        return accounts

    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM links")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if result == None:
        return 0
        
    accounts = []
    for link in result:
        if link[1] not in accounts:
            accounts.append(link[1])
    accounts = len(accounts)
    last_check_account = time.time()
    return accounts

def delete_token(token):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tokens WHERE token=%s", (token,))
    connection.commit()
    cursor.close()
    connection.close()
def delete_token_domain(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM tokens WHERE owner=%s", (domain,))
    connection.commit()
    cursor.close()
    connection.close()

def add_token(token,domain):
    # Delete any existing tokens with the same domain
    delete_token_domain(domain)
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO tokens (token,owner) VALUES (%s,%s)", (token,domain))
    connection.commit()
    cursor.close()
    connection.close()

def get_token(token):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT owner FROM tokens WHERE token=%s", (token,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result == None:
        return False
    return result[0]

def get_users_links(domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM links WHERE owner=%s", (domain,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if result == None:
        return False
    return result

def get_all_links():
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM links")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    if result == None:
        return False
    return result

def get_link(url):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("SELECT link FROM links WHERE url=%s", (url,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result == None:
        return False
    return result[0]

def add_link(url,link,domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO links (owner,url,link) VALUES (%s,%s,%s)", (domain,url,link))
    connection.commit()
    cursor.close()
    connection.close()

def delete_link(url,domain):
    connection = mysql.connector.connect(**dbargs)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM links WHERE url=%s AND owner=%s", (url,domain))
    connection.commit()
    cursor.close()
    connection.close()