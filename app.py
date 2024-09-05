import os
from functools import wraps
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask_moment import Moment
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)
moment = Moment(app)


# LOG IN REQUIRED 
def login_required(f):
    """
    Function to ensure that user is logged in

    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """
        https://flask.palletsprojects.com/en/2.3.x/patterns/viewdecorators/
        """
        if session.get("user") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


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


# WEBSITE VISITOR LANDING PAGE
@app.route("/", methods=["GET"])
@app.route("/index.html")
def index():
    """
    Function to render to homepage if not logged in
    """
    return render_template("index.html")


# NEW USER REGISTRATION
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


# USER PLOGIN PAGE
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
            flash("Incorrect Username and/or Password!!!!!")
            return redirect(url_for("login"))
        if password is None:
            flash("Incorrect Username and/or Password!!!!!")
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
            flash("Incorrect Username and/or Password!!!!!")
            return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password!!!!!")
            return redirect(url_for("login"))

    return render_template("login.html")


# USER/ADMIN CHANGE PASSWORD REQUEST
@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """
    Renders 'changepass.html' when request method is get.
    """
    if request.method == "POST":
        # Find username
        username = mongo.db.users.find_one(
            {"username": session["user"]})

        # Acquire form fields
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_new_password")

        # Validate that input is not empty
        if current_password and new_password and confirm_password is None:
            flash("Please complete the required fields")
            return redirect(url_for('changepass'))

        # Check to see if new_password and confirm_password is same
        if new_password == confirm_password:

            # Use check_password_hash to ensure that
            # the current password is the same as database
            if check_password_hash(username["password"], current_password):

                # Generate a new password hash:
                new_hash_password = generate_password_hash(new_password)

                # New entry to the database
                new_password_entry = {"password": new_hash_password}

                # Update database and return
                mongo.db.users.update_one(
                    {"username": session["user"]}, {"$set": new_password_entry}
                    )
                flash("Password succesfully changed!")
                return redirect(url_for('changepass'))

        flash("Changing password failed!")
        return render_template("changepass.html")

    return render_template("changepass.html")


# USER PROFILE DASHBOARD
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username == "systemadmin":
        users = mongo.db.users.find()
    else:
        users = mongo.db.users.find({"username": username})

    return render_template("profile.html", name=username,)


# USER PROFILE/IDENTITY INFORMATION
@app.route("/myinfo", methods=["GET", "POST"])
def myinfo():
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    if username == "systemadmin":
        users = mongo.db.users.find()
    else:
        users = mongo.db.users.find({"username": username})
        
    return render_template("myinfo.html", users=users)


# USER PROFILE/NEW TRAVEL REQUEST
@app.route("/newTravel", methods=["GET", "POST"])
def newTravel():
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if username == "systemadmin":
        travel_info = mongo.db.travel_info.find()
    else:
        travel_info = mongo.db.travel_info.find({"username": username})

    return render_template("newTravel.html", name=username,
                           travel_info=travel_info)


# USER UPDATE ACCOUNT OPTION 
@app.route("/update/<users_id>", methods=["GET", "POST"])
@login_required
def update(users_id):
    
    users = mongo.db.users.find_one({"_id": ObjectId(users_id)})
    if request.method == "POST":
        email = request.form.get("email")
        number = request.form.get("number")

        update_entry = {
            "username": users["username"],
            "email": email,
            "number": number,
        }

        users = mongo.db.users.find_one({"_id": ObjectId(users_id)})

        mongo.db.users.update_one({"_id": ObjectId(users_id)}, {"$set": update_entry}
            )
        flash("User Successfully Updated!")
        return redirect(url_for("myinfo", username=session["user"]))

    return render_template("update.html", users=users)


# CURRENT USER LOG IN REQUEST FORM
@app.route("/travel_info", methods=["GET", "POST"])
def travel_info():

    if request.method == "POST":
        travel_dates = request.form.get("travel_dates")
        flexible_dates = request.form.get("flexible_dates")
        include_flights = request.form.get("include_flights")
        flying_from = request.form.get("flying_from")
        number_adult_guests = request.form.get("number_adult_guests")
        number_kids_guests = request.form.get("number_kids_guests")
        preferred_accom = request.form.get("preferred_accom")
        rooms = request.form.get("rooms")
        concerts = request.form.get("concerts")
        activity = request.form.get("activity")
        guide = request.form.get("guide")
        contact = request.form.get("contact")
        message = request.form.get("message")

        travel_entry = {
            "username": session["user"],
            "travel_dates": travel_dates,
            "flexible_dates": flexible_dates,
            "include_flights": include_flights,
            "flying_from": flying_from,
            "number_adult_guests": number_adult_guests,
            "number_kids_guests": number_kids_guests,
            "preferred_accom": preferred_accom,
            "rooms" : rooms,
            "concerts": concerts,
            "activity": activity,
            "guide": guide,
            "contact": contact,
            "message": message,
        }
        
        mongo.db.travel_info.insert_one(travel_entry)
        flash("Travel Information Added!")
        return redirect(url_for("newTravel", username=session["user"]))
    else:
        airport = mongo.db.airport.find_one()
        return render_template("travel_info.html", airport=airport)


# CONTACT FORM 
@app.route("/contact", methods=["GET"])
def contact():
    """
    Render's contact page template
    """
    email_api = os.environ.get("EMAIL_API")
    return render_template("contact.html", email_api=email_api)


    #  ----------------ADMIN FUNCTIONALILITIES

# MANAGE USERS TEMPLATE
@app.route("/manageusers/<username>", methods=["GET"])
@login_required
def manageusers(username):

    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    if username == "systemadmin":
        users = mongo.db.users.find()

        return render_template("manageusers.html", users=users)


# DELETE USER (keeps showing 404, found solution from https://www.youtube.com/watch?v=Ya3zjAgQWQo)
@app.route(
    "/manageusers/<username>#deleteModal<user_name>", methods=["GET", "POST"]
)
@login_required
def delete_user(username, user_name):
            
    if request.method == "POST":
        username = mongo.db.users.find_one(
            {"username": session['user']})["username"]

        if username == "systemadmin":
            user = mongo.db.users.find_one(
                {"username": user_name}
            )
        
        if user and user_name != "systemadmin":
            mongo.db.users.delete_one({"username": user_name})

            flash("The user has been Deleted")
            return redirect(url_for("manageusers", username=session["user"]))

    return render_template("manageusers.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
