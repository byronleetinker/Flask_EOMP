import hmac
import sqlite3
from flask_mail import Mail, Message
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
    conn.close()


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
                     "category TEXT NOT NULL,"
                     "name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL)")
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
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'byronflasktask@gmail.com'
app.config['MAIL_PASSWORD'] = 'Tkinter0'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
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
        email = request.form['email']
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

            if response["status_code"] == 201:
                msg = Message('Success!', sender='byronflasktask@gmail.com', recipients=[email])
                msg.body = "Your registration has been successful"
                mail.send(msg)
                return "Message Sent"


@app.route('/create-product/', methods=["POST"])
def create_product():
    response = {}

    if request.method == "POST":
        category = request.form['category']
        name = request.form['name']
        price = request.form['price']
        content = request.form['description']

        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO product("
                           "category,"
                           "name,"
                           "price,"
                           "description) VALUES(?, ?, ?, ?)", (category, name, price, content))
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


@app.route("/delete-product/<int:product_id>/")
def delete_product(product_id):
    response = {}

    with sqlite3.connect("databases.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product Deleted Successfully."
    return response


@app.route('/view-one/<int:product_id>/')
def view_one_product(product_id):
    response = {}

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=?", str(product_id))
        product = cursor.fetchone()

        response['status_code'] = 200
        response['data'] = product
        return jsonify(response)


@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
# @jwt_required()
def edit_product(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('database.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("category") is not None:
                put_data["category"] = incoming_data.get("category")

                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE id=?", (put_data["category"], product_id))

                    conn.commit()
                    response['message'] = "Update Successfully"
                    response['status_code'] = 200

            elif incoming_data.get("name") is not None:
                put_data['name'] = incoming_data.get('name')

                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET name =? WHERE id=?", (put_data["name"], product_id))
                    conn.commit()

                    response["content"] = "Content Updated Successfully"
                    response["status_code"] = 200

            elif incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('database.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["content"] = "Content Updated Successfully"
                    response["status_code"] = 200

    return response


@app.route('/get-product/<int:product_id>/', methods=["GET"])
def get_post(product_id):
    response = {}

    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE id=" + str(product_id))

        response["status_code"] = 200
        response["description"] = "Product Retrieved Successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == "__main__":
    app.run()
    app.debug(True)
