import hmac
import sqlite3
from flask import *
from flask_jwt import *


class User(object):
    def __init__(self, user_id, username, password):
        self.user_id = user_id
        self.username = username
        self.password = password


# create user table
def init_user_table():
    conn = sqlite3.connect('shop.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "email_address TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")
    print("Users table created successfully")
    conn.close()


init_user_table()


# fetching users from the user table
def fetch_users():
    with sqlite3.connect('shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        registered_users = cursor.fetchall()

        new_data = []

        for data in registered_users:
            new_data.append(User(data[0], data[4], data[5]))
    return new_data


all_users = fetch_users()


username_table = {u.username: u for u in all_users}
userid_table = {u.user_id: u for u in all_users}


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

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# ap to register user
@app.route('/register/', methods=["POST"])
def registration():
    response = {}

    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email_address']
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users("
                           "first_name,"
                           "last_name,"
                           "email_address,"
                           "username,"
                           "password) VALUES(?, ?, ?, ?, ?)", (first_name, last_name, email, username, password))
            conn.commit()
            response["message"] = "Successful Registration"
            response["status_code"] = 201
        return response


class Products(object):
    def __init__(self, product_id, product_name, product_price, product_description, new_data):
        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price
        self.product_description = product_description
        self.new_data = new_data

    # creating products table
    def init_product_table(self):
        with sqlite3.connect('shop.db') as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS products (product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                         "product_name TEXT NOT NULL,"
                         "product_price TEXT NOT NULL,"
                         "product_quantity TEXT NOT NULL,"
                         "product_description TEXT NOT NULL)")
        print("Products table created successfully.")

        self.init_product_table()

    # route to add a product
    @app.route('/add-product/', methods=["POST"])
    @jwt_required()
    def add_product(self):
        response = {}

        if request.method == "POST":
            name = request.form['product_name']
            price = request.form['product_price']
            quantity = request.form['product_quantity']
            description = request.form['product_description']

            with sqlite3.connect('shop.db') as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO products("
                               "product_name,"
                               "product_price,"
                               "product_quantity"
                               "product_description) VALUES(?, ?, ?, ?)", (name, price, quantity, description))
                conn.commit()
                response["status_code"] = 201
                response['description_message'] = "Product added successfully"
            return response


# route to show all products
@app.route('/show-products/', methods=["GET"])
def show_products():
    # self.new_data = new_data
    products_data = []
    # response = {}
    with sqlite3.connect('shop.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

        for data in products:
            products_data.append(Products(data[0], data[1], data[2], data[3]))
        return products_data

        # response['status_code'] = 200
        # response['data'] = products
        # return response


all_products = show_products()

product_table = {p.product_name: p for p in all_products}
productId_table = {p.product_id: p for p in all_products}
productPrice_table = {p.product_price: p for p in all_products}
productDescription_table = {p.product_description: p for p in all_products}


# route to delete single product
@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_product(self, product_id):
    response = {}
    with sqlite3.connect("shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=" + str(product_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "Product deleted successfully."
    return response

# route to edit single product
@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(self, product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('shop.db'):  # as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('shop.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET product_name =? WHERE product_id=?", (put_data
                                                                                              ["product_name"],
                                                                                              product_id))
                    conn.commit()
                    response['message'] = "Product update was successful."
                    response['status_code'] = 200
            if incoming_data.get("product_price") is not None:
                put_data['product_price'] = incoming_data.get('product_price')

                with sqlite3.connect('shop.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE products SET product_price =? WHERE product_id=?", (put_data
                                                                                               ["product_price"],
                                                                                               product_id))
                    conn.commit()

                    response["product_price"] = "product_price updated successfully"
                    response["status_code"] = 200
    return response

# route to view single product
@app.route('/view-product/<int:product_id>/', methods=["GET"])
def view_product(self, product_id):
    response = {}

    with sqlite3.connect("shop.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products WHERE product_id=" + str(product_id))

        response["status_code"] = 200
        response["message_description"] = "Product retrieved successfully"
        response["data"] = cursor.fetchone()


if __name__ == "__main__":
    app.debug = True
    app.run()
