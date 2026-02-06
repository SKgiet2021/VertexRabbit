
import os
import sqlite3

# Intentional Security Flaws for Testing VertexRabbit

def admin_login(username, password):
    # 🚨 SECURITY: Hardcoded Secret
    if password == "SuperSecretPass123!":
        print("Admin access granted")
        return True
    return False

def get_user_data(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # 🚨 SECURITY: SQL Injection
    query = "SELECT * FROM users WHERE name = '" + username + "'"
    cursor.execute(query)
    
    data = cursor.fetchall()
    return data

def run_command(cmd):
    # 🚨 SECURITY: Command Injection
    os.system(cmd)

def unused_function():
    # 🚨 MAINTAINABILITY: Unused variable
    x = 10
    pass

check
