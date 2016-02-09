"""Movie Ratings."""
# Author : Erin Allard, Shai Wilson

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
    return render_template("users_list.html", users=users)



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


    if email_in_DB:
        check_password = User.query.filter(User.password==password, User.email==email).first()
        session['current_user'] = check_password.user_id
        user_id = check_password.user_id
        print "user_id", user_id
        # print session['current_user']
        # Show user success message on next page load
        flash("Successfully logged in!")
        return redirect("/users/%s" % user_id)
    else:
        flash("Hey! You're user_name or password is incorrect.")
        return redirect("/")



@app.route('/logout')
def logout():
    """Logout to an existing account.""" 
    
    if 'current_user' not in session:
        # print"hip hip hoorrraayy!! I'm EMPTY."
        flash("Hey! You're not even signed in!!!")
    else:
        print "The current_user: ", session['current_user']
        del session['current_user'] 
        flash("Successfully logged out!")

    # Redirect to home page
    return redirect("/")


@app.route('/account_status', methods=["POST"])
def account_status():
    """Return user account status."""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    is_user = User.query.filter_by(email=email).first()

    if is_user != None:  
        flash("Uh oh! You are already in the database!")
    else:     
        flash("Thanks! We have successfully created your account.") 
        add_new_user = User(email=email, password=password, age=age, zipcode=zipcode)
        db.session.add(add_new_user)
        db.session.commit()

    return render_template("status.html",
                            user=add_new_user)



@app.route('/user_list')
def show_users():
    """Show all users with accounts."""


    return render_template("login.html")



@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Return page showing the details of a given user."""

    user = User.query.get(user_id)
    user_id = user.user_id
    user_zipcode = user.zipcode
    user_age = user.age

    return render_template("user_details.html",
                           display_user_id=user_id,
                           display_user_zipcode=user_zipcode,
                           display_user_age=user_age)



@app.route("/movies")
def movie_list():
    """Show list of movies."""

    movies = Movie.query.all()
    return render_template("movies_list.html", movies=movies)


@app.route("/movies/<int:movie_id>")
def show_movie(movie_id):
    """Return page showing the details of a given movie."""

    movie = Movie.query.get(movie_id)
    movie_id = movie.movie_id
    movie_title = movie.title
    movie_url = movie.imdb_url

    movie_ratings = movie.ratings

    user_id = session['current_user']
    if user_id:
        user_rating = Rating.query.filter_by(
        movie_id=movie_id, user_id=user_id).first()
    else:
        user_rating = None

    # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            print user
            prediction = user.predict_rating(movie)


    return render_template("movie_details.html",
                           display_movie_id=movie_id,
                           display_movie_title=movie_title,
                           display_movie_url=movie_url,
                           movie_rating=movie_ratings,
                           user_rating=user_rating,
                           average=avg_rating,
                           prediction=prediction)


@app.route('/new_rating', methods=["POST"])
def add_new_rating():
    """Check to see if a rating is in the database."""
    movie_id = request.form.get("movie_id")
    movie = Movie.query.get(movie_id)
    movie_title = movie.title
    rating = request.form.get("new_rating")
    user_id = session['current_user']
    movie_ratings = movie.ratings

    existing_rating = Rating.query.filter(Rating.user_id == user_id, 
                                          Rating.movie_id == movie_id).all()

    if len(existing_rating) == 0:
            new_rating = Rating(score = rating,
                                user_id = user_id,
                                movie_id = movie_id)
            db.session.add(new_rating)
        
    else:
        existing_rating[0].score = rating
        db.session.commit()
        flash("Your rating was submitted.")

    return render_template("movie_details.html",
                           display_movie_id=movie_id,
                           display_movie_title=movie_title,
                           movie_rating=movie_ratings,
                           user_rating=rating)

    return "ok"


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()
