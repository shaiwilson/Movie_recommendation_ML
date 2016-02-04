"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask_debugtoolbar import DebugToolbarExtension

from flask import Flask, render_template, redirect, request, flash, session

from model import User, Rating, Movie, connect_to_db, db

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")



@app.route("/users")
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)



@app.route('/signup')
def signup():
    """Sign up for an account."""


    return render_template("signup.html")



@app.route('/login')
def login():
    """Login to an existing account."""


    return render_template("login.html")



@app.route('/logged_in', methods=["POST"])
def is_logged_in():
    """Check to see if a user is in the database."""

    email = request.form.get("email")
    password = request.form.get("password")

    email_in_DB = User.query.filter_by(email=email).first()
    print "check_email: ", email_in_DB

    if email_in_DB:
        check_password = User.query.filter(User.password==password, User.email==email).first()
        print "check_password: ", check_password.password
        
    return render_template("homepage.html")

# TODO:
# We finished our login in form!
# Error handle when user does not enter the correct password
#   return user to the login page
#   show a flash message that the user entered an incorrect password

# More GENERAL TODO:
    # Where we left off: added flask message to base.html
    # when the user logs in successfully, show a flash message of success on the user_list.html page
    # when an existing user attempts to login, show a flash message that they already have an accout: see line 100S


@app.route('/account_status', methods=["POST"])
def account_status():
    """Return user account status."""

    # logic for default account status
    account_descrip = "Thanks! We have successfully created your account."
    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    is_user = User.query.filter_by(email=email).first()

    if is_user != None:
        account_descrip = "Uh oh! You are already in the database!"  
        return account_descrip
        # further, redirect to login page
        # show a flash message that they already have an account
    else:      
        add_new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(add_new_user)
        db.session.commit()

    return render_template("status.html",
                            user=add_new_user,
                            description=account_descrip)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
