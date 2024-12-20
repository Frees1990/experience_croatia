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
    Decorator to ensure that the user is logged in.
    Redirects to the login page with a flash message if not logged in.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            flash("You need to log in to access this page.")
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


@app.route('/about')
def about():
    return render_template('about.html')


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


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Renders login template and handles user authentication.
    """
    if request.method == "POST":
        # Fetch form data
        username = request.form.get("username")
        password = request.form.get("password")

        # Validate inputs
        if not username or not password:
            flash("Username and/or Password cannot be empty!")
            return redirect(url_for("login"))

        # Check if username exists in database
        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            # Validate password
            if check_password_hash(existing_user["password"], password):
                session["user"] = username  # Initialize session
                flash("Welcome, {}".format(username))
                return redirect(url_for("profile", username=session["user"]))

            # Invalid password
            flash("Incorrect Username and/or Password!")
            return redirect(url_for("login"))

        # Username does not exist
        flash("Incorrect Username and/or Password!")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """
    Handles user password change requests.
    """
    if request.method == "POST":
        username = mongo.db.users.find_one({"username": session["user"]})
        
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_new_password")

        if not current_password or not new_password or not confirm_password:
            flash("Please complete the required fields")
            return redirect(url_for('changepass'))

        if new_password != confirm_password:
            flash("New password and confirmation do not match")
            return redirect(url_for('changepass'))
        
        if check_password_hash(username["password"], current_password):
            new_hash_password = generate_password_hash(new_password)
            mongo.db.users.update_one(
                {"username": session["user"]},
                {"$set": {"password": new_hash_password}}
            )
            flash("Password successfully changed!")
            return redirect(url_for('success'))

        flash("Current password is incorrect")
        return redirect(url_for('changepass'))

    return render_template("changepass.html")


@app.route("/success")
@login_required
def success():
    """
    Renders the success page after password change.
    """
    return render_template("success.html")


# USER PROFILE DASHBOARD
@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Ensure user is logged in
    if not session.get("user"):
        return redirect(url_for("login"))

    # Fetch the session user's details from the database
    user = mongo.db.users.find_one({"username": session["user"]})

    # Handle missing user
    if not user:
        return redirect(url_for("login"))

    # Get user's name and query users based on admin status
    name = user.get("name", "User")  # Default to "User" if name is missing
    if session["user"] == "systemadmin":
        users = mongo.db.users.find()
    else:
        users = mongo.db.users.find({"username": session["user"]})

    return render_template("profile.html", name=name, username=session["user"], users=users)


# USER PROFILE/IDENTITY INFORMATION
@app.route("/myinfo", methods=["GET", "POST"])
@login_required
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
@login_required  # Protect this route
def newTravel():
    user = mongo.db.users.find_one({"username": session["user"]})

    # Handle invalid user session (extra safety)
    if not user:
        flash("User not found. Please log in again.")
        return redirect(url_for("login"))

    username = user["username"]
    name = user.get("name", "Default Name")

    # Fetch travel information
    if username == "systemadmin":
        travel_info = mongo.db.travel_info.find()
    else:
        travel_info = mongo.db.travel_info.find({"username": username})

    # Handle POST actions (delete/update)
    if request.method == "POST":
        travel_info_id = request.form.get("travel_info_id")
        try:
            if travel_info_id:
                object_id = ObjectId(travel_info_id)
                if "delete" in request.form:
                    mongo.db.travel_info.delete_one({"_id": object_id})
                    flash("Request Deleted.")
                elif "update" in request.form and username != "systemadmin":
                    updated_data = {
                        "travel_dates": request.form.get("travel_dates", ""),
                        "email": request.form.get("email", ""),
                    }
                    mongo.db.travel_info.update_one({"_id": object_id}, {"$set": updated_data})
                    flash("Request Updated.")
            return redirect(url_for("newTravel"))
        except Exception as e:
            flash(f"An error occurred: {str(e)}")

    return render_template("newTravel.html", travel_info=travel_info, username=username, name=name)


@app.route("/updateTravel/<users_id>", methods=["GET", "POST"])
@login_required
def updateTravel(users_id):
    # Fetch the travel info from the database by its ID
    travel_info = mongo.db.travel_info.find_one({"_id": ObjectId(users_id)})

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
        mongo.db.travel_info.update_one({"_id": ObjectId(users_id)}, {"$set": updated_data})

        flash("Travel Request Updated Successfully", "success")

        # Redirect to the newTravel page where the updated card will be displayed
        return redirect(url_for("newTravel"))

    # If GET request, just render the form with current data
    return render_template("updateTravel.html", travel_info=travel_info, users_id=users_id)


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
        nights = request.form.get("nights")
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
            "nights": nights,
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


@app.route("/contact", methods=["GET"])
def contact():
    return render_template("contact.html")


@app.route("/thank_you", methods=["GET"])
def thank_you():
    return render_template("thank_you.html")
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
            debug=False)