import os
from functools import wraps
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


@app.route("/", methods=["GET"])
@app.route("/index.html")
def index():
    """
    Function to render to homepage if not logged in
    """
    return render_template("index.html")


@app.route("/userdoesnotexist.html")
def userdoesnotexist():
    """
    Function to render to homepage if not logged in
    """
    return render_template("userdoesnotexist.html")


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
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """

    Renders template for 'login'.

    looks up user details in MongoDB collection users

    """
    if request.method == "POST":
        # Validate that username and password is not an empty string:
        username = request.form.get("username")
        password = request.form.get("password")
        if username is None:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))
        if password is None:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": username}
        )

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(existing_user["password"], password):
                session["user"] = username
                flash("Welcome, {}".format(username))
                return redirect(url_for(
                    "profile", username=session["user"]
                ))
                # invalid password match
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Username does not exist")
            return redirect(url_for("userdoesnotexist"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["name"]
    return render_template("profile.html", name=username)


@app.route("/travel_info", methods=["GET", "POST"])
def travel_info():

    if request.method == "POST":
        travel_dates = request.form.get("travel_dates")
        flexible_dates = request.form.get("flexible_dates")
        include_flights = request.form.get("include_flights")
        flying_from = request.form.get("flying_from")
        number_adult_guests = request.form.get("number_adult_guests")
        number_kids_guests = request.form.get("number_kids_guests")
        include_concerts = request.form.get("include_concerts")
        include_excursions = request.form.get("include_excursions")
        include_guide = request.form.get("include_guide")
        preferred_contact = request.form.get("preferred_contact")
        other_info = request.form.get("other_info")

        info_entry =  {
            "username": session["user"],
            "travel_dates": (travel_dates),
            "flexible_dates": flexible_dates,
            "include_flights": include_flights,
            "flying_from": flying_from,
            "number_adult_guests": number_adult_guests,
            "number_kids_guests": number_kids_guests,
            "include_concerts": include_concerts,
            "include_excursions": include_excursions,
            "include_guide": include_guide,
            "preferred_contact": preferred_contact,
            "other_info": other_info,
        }

        mongo.db.travel_info.insert_one(info_entry)
        flash("Travel Information Added!")
        return redirect(url_for("profile", username=session["user"]))
    else:
        return render_template("travel_info.html", travel_info=travel_info)


# LOGOUT
@app.route("/logout")
def logout():
    """
    Removes user session.

    Redirects to login page

    """
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/contact", methods=["GET"])
def contact():
    """
    Render's contact page template
    """
    email_api = os.environ.get("EMAIL_API")
    return render_template("contact.html", email_api=email_api)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)