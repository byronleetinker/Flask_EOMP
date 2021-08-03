import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def init_user_table():
    conn = sqlite3.connect('database.db')
    print("Opened Database Successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "name TEXT NOT NULL,"
                 "surname TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("User Table Created Successfully")


init_user_table()


def fetch_users():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


users = fetch_users()


def init_product_table():
    with sqlite3.connect('database.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product(id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "category TEXT NOT NULL)")
        conn.commit()
    print("Product Table Created Successfully.")
    conn.close()


init_product_table()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
CORS(app)

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/registration/', methods=["POST"])
def registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['name']
        last_name = request.form['surname']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user("
                           "name,"
                           "surname,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?)", (first_name, last_name, username, password))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/create-product/', methods=["POST"])
def create_product():
    response = {}

    if request.method == "POST":
        name = request.form['name']
        price = request.form['price']
        content = request.form['content']
        category = request.form['category']

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO product("
                           "name,"
                           "price,"
                           "content,"
                           "category) VALUES(?, ?, ?, ?)", (name, price, content, category))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Product Table Added Successfully"
        return response


@app.route('/get-product/', methods=["GET"])
def get_product():
    response = {}
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    response = {}
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product Deleted Successfully."
    return response


@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('database.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    print(put_data["title"])
                    print("UPDATE product SET title =? WHERE id=?", (put_data["title"], product_id))
                    cursor.execute("UPDATE product SET title =? WHERE id=?", (put_data["title"], product_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data.get("content") is not None:
                put_data['content'] = incoming_data.get('content')

                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET content =? WHERE id=?", (put_data["content"], product_id))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/get-product/<int:product_id>/', methods=["GET"])
def get_post(product_id):
    response = {}

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=" + str(product_id))

        response["status_code"] = 200
        response["description"] = "product retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.run()
    app.debug(True)