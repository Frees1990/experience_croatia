import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_request")
def get_request():
    request = mongo.db.request.find()
    return render_template("request.html", request=request)


@app.route("/index.html")
def index():
    """
    Function to render to homepage if not logged in
    """
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Renders template for 'registration'

    Adds new user to MongoDB collect 'Users' then redirects to profile

    """
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        # Grab variables from form:

        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        #  Registration form validation
        if [name, email, number, username, password, confirm_password] is None:
            flash("Registration failed: Please complete the required fields")
            return redirect(url_for("register"))
        if len(username) < 5 or len(username) > 30:
            flash("Registration failed: Please complete the required fields")
            return redirect(url_for("register"))
        # https://www.w3schools.com/python/ref_string_isalnum.asp
        if not password.isalnum() and len(password) < 8:
            flash("Registration failed: Please complete the required fields")
            return redirect(url_for("register"))
        if password != confirm_password:
            flash("Registration failed: Please complete the required fields")
            return redirect(url_for("register"))
        register = {
            "name": request.form.get("name").lower(),
            "email": request.form.get("email").lower(),
            "number": request.form.get("number"),
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
    return render_template("register.html")

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)