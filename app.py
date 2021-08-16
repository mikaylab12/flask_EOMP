import hmac
import sqlite3
from smtplib import SMTPRecipientsRefused

from flask import *
from flask_jwt import *
from flask_cors import *
from flask_mail import Mail, Message
from datetime import timedelta


# creating a user object
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# initializing the database
class Database(object):
    def __init__(self):
        self.conn = sqlite3.connect('shop.db')
        self.cursor = self.conn.cursor()

    # to commit multiple things
    def to_commit(self, query, values):
        self.cursor.execute(query, values)
        self.conn.commit()

    # one commit
    def single_commit(self, query):
        self.cursor.execute(query)

    # to fetch all
    def fetch_all(self):
        return self.cursor.fetchall()

    # to fetch one
    def fetch_one(self):
        return self.cursor.fetchone()


# create user table
def init_user_table():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    print("Opened database successfully")
    cursor.execute("CREATE TABLE IF NOT EXISTS users "
                   "(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "first_name TEXT NOT NULL,"
                   "last_name TEXT NOT NULL, "
                   "email_address TEXT NOT NULL, "
                   "username TEXT NOT NULL, "
                   "password TEXT NOT NULL)")
    print("Users table created successfully")
    conn.close()


# calling function to create users table
init_user_table()


# fetching users from the user table
def fetch_users():
    db = Database()
    query = "SELECT * FROM users"
    db.single_commit(query)
    registered_users = db.fetch_all()

    new_data = []

    for data in registered_users:
        new_data.append(User(data[0], data[4], data[5]))
    return new_data


# calling function to fetch all users
all_users = fetch_users()


username_table = {u.username: u for u in all_users}
userid_table = {u.id: u for u in all_users}


# function to get unique token upon registration
def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# function to identify user
def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


# initializing app
app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'
app.config["JWT_EXPIRATION_DELTA"] = timedelta(days=1)  # allows token to last a day
app.config['MAIL_SERVER'] = 'smtp.gmail.com'            # server for email to be sent on
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mikayladummy2@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dummy123!'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


# route to register user
@app.route('/register/', methods=["POST"])
def registration():
    response = {}
    db = Database()
    try:
        if request.method == "POST":

            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email_address']
            username = request.form['username']
            password = request.form['password']

            query = "INSERT INTO users(first_name, last_name, email_address,username, password) VALUES(?, ?, ?, ?, ?)"
            values = (first_name, last_name, email, username, password)
            db.to_commit(query, values)

            msg = Message('Welcome Email', sender='mikayladummy2@gmail.com', recipients=[email])
            # message for the email
            msg.body = "Hello " + str(email) + \
                       "\n\nThank you for registering with us! \n\nWe look forward to doing business with you. " \
                       "\n\nRegards"
            mail.send(msg)

            response["message"] = "Successful Registration"
            response["status_code"] = 201
            return response
    except SMTPRecipientsRefused:
        response['message'] = "Please enter a valid email address."
        response['status_code'] = 400
        return response


@app.route('/edit-user/<int:user_id>/', methods=["PUT"])
# @jwt_required()
def edit_user(user_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        with sqlite3.connect('shop.db'):
            data_receive = dict(request.json)
            put_data = {}

            if data_receive.get("first_name") is not None:
                put_data["first_name"] = data_receive.get("first_name")
                query = "UPDATE users SET first_name =? WHERE user_id=?"
                values = (put_data["first_name"], str(user_id))
                db.to_commit(query, values)

                response['message'] = "First name update was successful."
                response['status_code'] = 200
            if data_receive.get("last_name") is not None:
                put_data['last_name'] = data_receive.get('last_name')
                query = "UPDATE users SET last_name =? WHERE user_id=?"
                values = (put_data["last_name"], str(user_id))
                db.to_commit(query, values)

                response["last_name"] = "Last name updated successfully"
                response["status_code"] = 200
            if data_receive.get("email_address") is not None:
                put_data['email_address'] = data_receive.get('email_address')
                query = "UPDATE users SET email_address =? WHERE user_id=?"
                values = (put_data["email_address"], str(user_id))
                db.to_commit(query, values)

                response["email_address"] = "Email address updated successfully"
                response["status_code"] = 200
            if data_receive.get("username") is not None:
                put_data['username'] = data_receive.get('username')
                query = "UPDATE users SET username =? WHERE user_id=?"
                values = (put_data["username"], str(user_id))
                db.to_commit(query, values)

                response["username"] = "Username updated successfully"
                response["status_code"] = 200
            if data_receive.get("password") is not None:
                put_data['password'] = data_receive.get('password')
                query = "UPDATE users SET password =? WHERE user_id=?"
                values = (put_data["password"], str(user_id))
                db.to_commit(query, values)

                response["password"] = "Password updated successfully"
                response["status_code"] = 200
            return response


@app.route('/show-users/', methods=["GET"])
def show_users():
    response = {}
    db = Database()
    query = "SELECT * FROM users"
    db.single_commit(query)
    products = db.fetch_all()

    response['status_code'] = 200
    response['data'] = products
    return response


# calling function to show all products
all_users = show_users()


@app.route("/delete-user/<int:user_id>")
# @jwt_required()
def delete_user(user_id):
    response = {}
    db = Database()
    query = "DELETE FROM users WHERE user_id=" + str(user_id)
    db.single_commit(query)
    response['status_code'] = 200
    response['message'] = "User deleted successfully."
    return response


# admin
# creating a user object
class Admin(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


# create admin table
def init_admin_table():
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    print("Opened database successfully")
    cursor.execute("CREATE TABLE IF NOT EXISTS admin "
                   "(admin_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                   "admin_name TEXT NOT NULL,"
                   "admin_surname TEXT NOT NULL, "
                   "admin_email TEXT NOT NULL, "
                   "admin_username TEXT NOT NULL, "
                   "admin_password TEXT NOT NULL)")
    print("Admin table created successfully")
    conn.close()


# calling function to create users table
init_admin_table()


# fetching admin users from the admin table
def fetch_admin():
    db = Database()
    query = "SELECT * FROM admin"
    db.single_commit(query)
    registered_admin = db.fetch_all()

    new_data = []

    for data in registered_admin:
        new_data.append(User(data[0], data[4], data[5]))
    return new_data


# calling function to fetch all users
all_admin = fetch_admin()


admin_username_table = {u.username: u for u in all_admin}
adminId_table = {u.id: u for u in all_admin}


@app.route('/register-admin/', methods=["POST"])
def admin_registration():
    response = {}
    db = Database()
    try:
        if request.method == "POST":

            first_name = request.form['admin_name']
            last_name = request.form['admin_surname']
            email = request.form['admin_email']
            username = request.form['admin_username']
            password = request.form['admin_password']

            query = "INSERT INTO admin(admin_name, admin_surname, admin_email,admin_username, admin_password) " \
                    "VALUES(?, ?, ?, ?, ?)"
            values = (first_name, last_name, email, username, password)
            db.to_commit(query, values)

            msg = Message('Welcome Email', sender='mikayladummy2@gmail.com', recipients=[email])
            # message for the email
            msg.body = "Hello " + str(email) + \
                       "\n\nThank you for registering as an Admin User! \n\nRegards"
            mail.send(msg)

            response["message"] = "Successful Registration"
            response["status_code"] = 201
            return response
    except SMTPRecipientsRefused:
        response['message'] = "Please enter a valid email address."
        response['status_code'] = 400
        return response


@app.route('/login-admin/', methods=["POST"])
def admin_login():
    response = {}
    db = Database()
    if request.method == "POST":
        username = request.json['admin_username']
        password = request.json['admin_password']
        conn = sqlite3.connect("shop.db")
        cur = conn.cursor()
        query = f"SELECT FROM admin WHERE admin_username= '{username}' and admin_password = '{password}' " \
                "VALUES(?, ?, ?, ?, ?)"
        db.single_commit(query)

        if not cur.fetchone():
            response['message'] = "Please enter valid credentials."
            response['status_code'] = 400
            return response
        else:
            response['message'] = "Welcome Admin"
            response['status_code'] = 200
            return response
    else:
        return "Wrong Method"


# creating products object
class Products(object):
    def __init__(self, product_id, product_name, product_price, product_description):
        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price
        self.product_description = product_description


# creating products table
def init_product_table():
    db = Database()
    query = ("CREATE TABLE IF NOT EXISTS products "
             "(product_id INTEGER PRIMARY KEY AUTOINCREMENT, "
             "product_name TEXT NOT NULL, "
             "product_price TEXT NOT NULL, "
             "product_quantity TEXT NOT NULL, "
             "product_description TEXT NOT NULL, "
             "product_image TEXT NOT NULL,"
             "total TEXT NOT NULL)")
    db.single_commit(query)
    print("Products table created successfully.")


# calling function to create products table
init_product_table()


# route to add a product
@app.route('/add-product/', methods=["POST"])
@jwt_required()
def add_product():
    response = {}
    db = Database()
    if request.method == "POST":
        name = request.json['product_name']
        price = request.json['product_price']
        quantity = request.json['product_quantity']
        description = request.json['product_description']
        image = request.json['product_image']
        total = int(price) * int(quantity)
        if name == '' or price == '' or quantity == '' or description == '' or image == '':
            return "Please fill in all entry fields"
        else:
            query = "INSERT INTO products( product_name, product_price, product_quantity, product_description, product_image, total)" \
                    "VALUES(?, ?, ?, ?, ?, ?)"
            values = (name, price, quantity, description, image, total)
            db.to_commit(query, values)

            response["status_code"] = 201
            response['description_message'] = "Product added successfully"
            return response


# route to show all products
@app.route('/show-products/', methods=["GET"])
def show_products():
    response = {}
    db = Database()
    query = "SELECT * FROM products"
    db.single_commit(query)
    products = db.fetch_all()

    response['status_code'] = 200
    response['data'] = products
    return response


# calling function to show all products
all_products = show_products()


# route to delete single existing product using product ID
@app.route("/delete-product/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    response = {}
    db = Database()
    query = "DELETE FROM products WHERE product_id=" + str(product_id)
    db.single_commit(query)
    response['status_code'] = 200
    response['message'] = "Product deleted successfully."
    return response


# route to edit single existing product using product ID
@app.route('/edit-product/<int:product_id>/', methods=["PUT"])
@jwt_required()
def edit_product(product_id):
    response = {}
    db = Database()

    if request.method == "PUT":
        with sqlite3.connect('shop.db'):
            data_received = dict(request.json)
            put_data = {}

            if data_received.get("product_name") is not None:
                put_data["product_name"] = data_received.get("product_name")
                query = "UPDATE products SET product_name =? WHERE product_id=?"
                values = (put_data["product_name"], product_id)
                db.to_commit(query, values)

                response['message'] = "Product update was successful."
                response['status_code'] = 200
            if data_received.get("product_price") is not None:
                put_data['product_price'] = data_received.get('product_price')
                query = "UPDATE products SET product_price =? WHERE product_id=?"
                values = (put_data["product_price"], str(product_id))
                db.to_commit(query, values)

                response["product_price"] = "Product price updated successfully"
                response["status_code"] = 200
            if data_received.get("product_quantity") is not None:
                put_data['product_quantity'] = data_received.get('product_quantity')
                query = "UPDATE products SET product_quantity =? WHERE product_id=?"
                values = (put_data["product_quantity"], str(product_id))
                db.to_commit(query, values)

                response["product_quantity"] = "Product quantity updated successfully"
                response["status_code"] = 200
            if data_received.get("product_description") is not None:
                put_data['product_description'] = data_received.get('product_description')
                query = "UPDATE products SET product_description =? WHERE product_id=?"
                values = (put_data["product_description"], str(product_id))
                db.to_commit(query, values)

                response["product_description"] = "Product description updated successfully"
                response["status_code"] = 200
            if data_received.get("product_image") is not None:
                put_data['product_image'] = data_received.get('product_image')
                query = "UPDATE products SET product_image =? WHERE product_id=?"
                values = (put_data["product_image"], str(product_id))
                db.to_commit(query, values)

                response["product_image"] = "Product image updated successfully"
                response["status_code"] = 200
            if data_received.get("total") is not None:
                put_data['total'] = data_received.get('total')
                query = "UPDATE products SET total =? WHERE product_id=?"
                values = (put_data["total"], str(product_id))
                db.to_commit(query, values)

                response["total"] = "The total updated successfully"
                response["status_code"] = 200
            return response


# route to view single profile
@app.route('/view-profile/<username>/', methods=["GET"])
def view_profile(username):
    response = {}
    if request.method == "GET":
        with sqlite3.connect("shop.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username='" + username + "'")
            data = cursor.fetchall()
            if data == []:
                return "User does not exit"
            else:
                response['message'] = 200
                response['data'] = data
        return response


# route to view single existing product using product ID
@app.route('/view-product/<int:product_id>/', methods=["GET"])
def view_product(product_id):
    response = {}
    db = Database()
    query = ("SELECT * FROM products WHERE product_id=" + str(product_id))
    db.single_commit(query)
    response["status_code"] = 200
    response["message_description"] = "Product retrieved successfully"
    response["data"] = db.fetch_one()
    return response


if __name__ == "__main__":
    app.debug = True
    app.run()
