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
        # further study, render movies page and show a flash message that 
        # they are already a user who is now logged in 
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
