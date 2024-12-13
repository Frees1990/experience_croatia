import os
import smtplib
from functools import wraps
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


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
@app.route("/")
@app.route("/index.html")
def index():
    """
    Render the homepage.
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
    # Fetch the session user's details from the database
    user = mongo.db.users.find_one({"username": session["user"]})

    # Redirect or handle missing user
    if not user:
        return redirect(url_for("login"))  # Redirect to login or appropriate page

    # Get user's name and decide query based on admin status
    name = user.get("name", "User")  # Fallback to "User" if name is missing
    if session["user"] == "systemadmin":
        users = mongo.db.users.find()
    else:
        users = mongo.db.users.find({"username": session["user"]})

    return render_template("profile.html", name=name, users=users)


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


@app.route("/newTravel", methods=["GET", "POST"])
def newTravel():
    user = mongo.db.users.find_one({"username": session["user"]})
    username = user["username"]
    name = user.get("name", "Default Name")
    # Determine the travel info to display
    if username == "systemadmin":
        travel_info = mongo.db.travel_info.find()
    else:
        travel_info = mongo.db.travel_info.find({"username": username})

    # Handle POST requests for delete and update
    if request.method == "POST":
        travel_info_id = request.form.get("travel_info_id")
        
        # Deletion
        if "delete" in request.form and travel_info_id:
            mongo.db.travel_info.delete_one({"_id": ObjectId(travel_info_id)})
            flash("Request Deleted")
            return redirect(url_for("travel"))

        # Update (only allowed for users, not admin)
        if "update" in request.form and travel_info_id and username != "systemadmin":
            updated_data = {
                "travel_dates": request.form.get("travel_dates"),
                "flexible_dates": request.form.get("flexible_dates"),
                "flying_from": request.form.get("flying_from"),
                "number_adult_guests": request.form.get("number_adult_guests"),
                "number_kids_guests": request.form.get("number_kids_guests"),
                "preferred_accom": request.form.get("preferred_accom"),
                "rooms": request.form.get("rooms"),
                "concerts": request.form.get("concerts"),
                "water_sports": request.form.get("water_sports"),
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
            }
            mongo.db.travel_info.update_one(
                {"_id": ObjectId(travel_info_id)},
                {"$set": updated_data}
            )
            flash("Travel request updated successfully!")
            return redirect(url_for("travel"))

    return render_template("newTravel.html", travel_info=travel_info, username=username, name=name)


@app.route("/updateTravel/<id>", methods=["GET", "POST"])
def updateTravel(id):
    # Fetch the travel info from the database by its ID
    travel_info = mongo.db.travel_info.find_one({"_id": ObjectId(id)})

    # If the method is POST, update the travel info
    if request.method == "POST":
        updated_data = {
            "travel_dates": request.form["travel_dates"],
            "flexible_dates": request.form["flexible_dates"],
            "flying_from": request.form["flying_from"],
            "number_adult_guests": request.form["number_adult_guests"],
            "number_kids_guests": request.form["number_kids_guests"],
            "preferred_accom": request.form["preferred_accom"],
            "rooms": request.form["rooms"],
            "concerts": request.form["concerts"],
            "water_sports": request.form["water_sports"],
            "email": request.form["email"],
            "phone": request.form["phone"],
        }
        
        # Update the travel_info in the database
        mongo.db.travel_info.update_one({"_id": ObjectId(id)}, {"$set": updated_data})

        flash("Travel Request Updated Successfully", "success")

        # Redirect to the newTravel page where the updated card will be displayed
        return redirect(url_for("newTravel"))

    # If GET request, just render the form with current data
    return render_template("updateTravel.html", travel_info=travel_info)


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
        flying_from = request.form.get("flying_from")
        number_adult_guests = request.form.get("number_adult_guests")
        number_kids_guests = request.form.get("number_kids_guests")
        preferred_accom = request.form.get("preferred_accom")
        rooms = request.form.get("rooms")
        concerts = request.form.get("concerts")
        water_sports = request.form.get("water_sports")
        email = request.form.get("email")
        phone = request.form.get("phone")
        DateTime = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")  # Fixed formatting for datetime

        travel_entry = {
            "username": session["user"],
            "travel_dates": travel_dates,
            "flexible_dates": flexible_dates,
            "flying_from": flying_from,
            "number_adult_guests": number_adult_guests,
            "number_kids_guests": number_kids_guests,
            "preferred_accom": preferred_accom,
            "rooms": rooms,
            "concerts": concerts,
            "water_sports": water_sports,
            "email": email,
            "phone": phone,
            "date": DateTime,
        }

        mongo.db.travel_info.insert_one(travel_entry)
        flash("Your request has been submitted to one of our Travel Guides and will get back to you with your perfect holiday plan to Pula Croatia.")
        return redirect(url_for("newTravel", username=session["user"]))
    else:
        # Hardcoded list of UK airports
        uk_airports = [
            {"Name": "Heathrow Airport", "IATA": "LHR"},
            {"Name": "Gatwick Airport", "IATA": "LGW"},
            {"Name": "Manchester Airport", "IATA": "MAN"},
            {"Name": "Birmingham Airport", "IATA": "BHX"},
            {"Name": "Edinburgh Airport", "IATA": "EDI"},
            {"Name": "Glasgow Airport", "IATA": "GLA"},
            {"Name": "Bristol Airport", "IATA": "BRS"},
            {"Name": "London City Airport", "IATA": "LCY"},
            {"Name": "Luton Airport", "IATA": "LTN"},
            {"Name": "Stansted Airport", "IATA": "STN"},
        ]
        return render_template("travel_info.html", airports=uk_airports)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # Process form data
        name = request.form.get("name")
        email = request.form.get("email")
        number = request.form.get("number", "")
        message = request.form.get("message")

    # Serve the contact page for GET requests
    return render_template("contact.html")
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


# DELETE REQUEST
@app.route("/managereq/<travel_info_id>#deleteModal", methods=["GET", "POST"])
@login_required
def delete_req(travel_info_id):
    if request.method == "POST":
        username = mongo.db.users.find_one({"username": session['user']})["username"]
        
        # Find the travel request by ObjectId
        travel_request = mongo.db.travel_info.find_one({"_id": ObjectId(travel_info_id)})

        if travel_request:
            mongo.db.travel_info.delete_one({"_id": ObjectId(travel_info_id)})
            flash("Request Deleted")
        
        if username == "systemadmin":
            return redirect(url_for("managereq"))
        else:
            return redirect(url_for("managereq", username=session["user"]))

    return render_template("managereq.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
