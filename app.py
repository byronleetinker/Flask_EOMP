import sqlite3
from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def user_table():
    conn = sqlite3.connect('final.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "surname TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


user_table()


def product_table():
    conn = sqlite3.connect('final.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "product_name TEXT NOT NULL,"
                 "product_price TEXT NOT NULL,"
                 "product_number TEXT NOT NULL,"
                 "product_type TEXT NOT NULL)")
    print("Product Table Created Successfully")
    conn.close()


product_table()

app = Flask(__name__)
app.debug = True


if __name__ == "__main__":
    app.run(debug=True)
