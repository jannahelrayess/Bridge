import os
from cs50 import SQL
import datetime
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import (
    login_required,
    is_strong_password,
    apology,
    get_like_count,
    get_comments,
    get_username,
    get_formatted_date,
    get_user_profile,
    update_data_image,
)
import base64


app = Flask(__name__)
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///bridge.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show the homepage and allow the user to go to login, register if he wants to."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM user WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["password"], request.form.get("password")
        ):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # Query database for all countries and colleges
    countries = db.execute("SELECT * FROM country")
    colleges = db.execute("SELECT * FROM college")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        username = request.form.get("username")
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        country_id = request.form.get("country")
        college_id = request.form.get("college")

        # Check if any field is blank
        if (
            not username
            or not fname
            or not lname
            or not email
            or not password
            or not confirmation
            or not country_id
            or not college_id
        ):
            return apology("All fields must be filled", 400)

        # Check if the user with such username already exists
        user_exists = db.execute("SELECT id FROM user WHERE username = ?", username)
        if user_exists:
            return apology("A user with that username already exists", 400)

        # Check if the password is strong
        if not is_strong_password(password):
            return apology(
                "Password must be at least 8 characters long and include a mix of letters, numbers, and symbols",
                400,
            )

        # Check if password and confirmation match
        if password != confirmation:
            return apology("Password and Confirmation fields do not match", 400)

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Insert the user into the database
        db.execute(
            "INSERT INTO user (username, fname, lname, email, password, country_id, college_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
            username,
            fname,
            lname,
            email,
            hashed_password,
            country_id,
            college_id,
        )

        # Query database user id
        user_id = db.execute("SELECT id FROM user WHERE username = ?", username)[0][
            "id"
        ]

        # Create space in database to store user's profile questions and socials
        db.execute("INSERT INTO profile_questions (user_id) VALUES (?)", user_id)

        db.execute("INSERT INTO socials (user_id) VALUES (?)", user_id)

        # Log user in
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", colleges=colleges, countries=countries)


@app.route("/user_profile", methods=["GET", "POST"])
@login_required
def user_profile():
    """Show profile of a user."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        user_id = request.form.get("user_id")

        # Use helper function to get user data
        user_dict = get_user_profile(user_id)

        # Use helper function to add user's image to data
        user_dict = update_data_image(user_dict)

        return render_template("profile.html", data=user_dict)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return redirect("/connect")


@app.route("/my_profile")
@login_required
def profile():
    """Show profile of current user."""

    # Retrieve current logged in user's id
    user_id = session.get("user_id")

    # Use helper function to get user data
    user_dict = get_user_profile(user_id)

    # Use helper function to add user's image to data
    user_dict = update_data_image(user_dict)

    return render_template("profile.html", data=user_dict, edit=True)


@app.route("/edit_profile", methods=["POST", "GET"])
@login_required
def edit_profile():
    """Allow user to edit their profile data."""

    # Retrieve current logged in user's id
    user_id = session.get("user_id")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        bio = request.form.get("bio")
        location = request.form.get("location")
        answer1 = request.form.get("question1")
        answer2 = request.form.get("question2")
        answer3 = request.form.get("question3")
        instagram = request.form.get("instagram")
        facebook = request.form.get("facebook")
        linkedin = request.form.get("linkedin")

        # Update user's profile question answers'
        db.execute(
            "INSERT OR REPLACE INTO profile_questions (answer1, answer2, answer3, user_id) VALUES (?, ?, ?, ?)",
            answer1,
            answer2,
            answer3,
            user_id,
        )

        # Update user's socials
        db.execute(
            "INSERT OR REPLACE INTO socials (instagram, facebook, linkedin, user_id) VALUES (?, ?, ?, ?)",
            instagram,
            facebook,
            linkedin,
            user_id,
        )

        # Update user's profile
        db.execute(
            "UPDATE user SET fname = ?, lname = ?, email = ?, image = ?, bio = ?, location = ? WHERE id = ?",
            fname,
            lname,
            email,
            request.files["image"].read() if "image" in request.files else None,
            bio,
            location,
            user_id,
        )

        return redirect("/my_profile")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Query database for all countries and colleges
        countries = db.execute("SELECT * FROM country")
        colleges = db.execute("SELECT * FROM college")

        return render_template(
            "edit_profile.html",
            data=get_user_profile(user_id),
            colleges=colleges,
            countries=countries,
        )


@app.route("/feed")
@login_required
def feed():
    """Display an interactive feed page with posts that users can comment and like."""

    # Retrieve posts from the database in order of relevance
    posts = db.execute(
        "SELECT id, image, caption, likes, created_at, user_id FROM post ORDER BY created_at DESC"
    )

    # Extract necessary data for each post
    formatted_posts = []

    for post in posts:
        image_b64 = base64.b64encode(post["image"]).decode("utf-8")
        formatted_post = {
            "id": post["id"],
            "image": image_b64,
            "likes": post["likes"],
            "created_at": post["created_at"],
            "caption": post["caption"],
            "user_name": get_username(post["user_id"]),
            "user_id": post["user_id"],
            "like_count": get_like_count(post["id"]),
            "comments": get_comments(post["id"]),
        }
        formatted_posts.append(formatted_post)

    return render_template(
        "feed.html", posts=formatted_posts, get_formatted_date=get_formatted_date
    )


@app.route("/create_post", methods=["POST", "GET"])
@login_required
def create_post():
    """A form where the user can create a post."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        caption = request.form.get("caption")
        image = request.files["image"]

        # Add post data to database
        image_data = image.read()

        db.execute(
            "INSERT INTO post (caption, image, created_at, user_id) VALUES (?, ?, ?, ?)",
            caption,
            image_data,
            datetime.datetime.now(),
            session["user_id"],
        )

        return redirect(url_for("feed"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("create_post.html")


@app.route("/like_post/<int:post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    """Stores the current user liking a post."""

    # Retrieve current logged in user's id
    user_id = session.get("user_id")

    # Query database to see if user has already liked this post
    liked_post = db.execute(
        "SELECT * FROM post_like WHERE post_id = ? AND user_id = ?", post_id, user_id
    )

    # If not liked, insert a new record into post_like
    if not liked_post:
        db.execute(
            "INSERT INTO post_like (post_id, user_id) VALUES (?, ?)", post_id, user_id
        )

    # Retrieve current number of likes
    likes = db.execute(
        "SELECT COUNT(*) AS num FROM post_like WHERE post_id = ?", post_id
    )[0]["num"]

    # Update number of likes for the post
    db.execute("UPDATE post SET likes = ? WHERE id = ?", likes, post_id)

    return redirect(url_for("feed"))


@app.route("/comment_post/<int:post_id>", methods=["POST"])
@login_required
def comment_post(post_id):
    """Stores the current user commenting on a post."""

    # Retrieve current logged in user's id
    user_id = session.get("user_id")

    # Retrieve comment from form
    comment_content = request.form.get("comment")

    # Insert new record of comment into post_comment
    db.execute(
        "INSERT INTO post_comment (post_id, user_id, content) VALUES (?, ?, ?)",
        post_id,
        user_id,
        comment_content,
    )

    return redirect(url_for("feed"))


@app.route("/connect", methods=["GET", "POST"])
@login_required
def connect():
    """Display a searchable page with all the users."""

    # Query database for all countries and colleges
    countries = db.execute("SELECT * FROM country")
    colleges = db.execute("SELECT * FROM college")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        country_id = request.form.get("country")
        college_id = request.form.get("college")
        username_query = request.form.get("username")

        # Initialize the search query and placeholders
        query = "SELECT username, fname, lname, id, image FROM user WHERE 1"
        placeholders = []

        # Add conditions for non-empty parameters
        if country_id != "":
            query += " AND country_id = ?"
            placeholders.append(country_id)

        if college_id != "":
            query += " AND college_id = ?"
            placeholders.append(college_id)

        if username_query != "":
            query += " AND username LIKE ?"
            placeholders.append(username_query)

        query += ";"

        # Execute the search query with dynamic placeholders
        people = db.execute(query, *placeholders)

        # Use helper function to add users' images to data
        for person in people:
            update_data_image(person)

        return render_template(
            "connect.html", people=people, countries=countries, colleges=colleges
        )

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # If given no specific search parameters, display all the users
        people = db.execute("SELECT * FROM user")

        # Use helper function to add users' images to data
        for person in people:
            update_data_image(person)

        return render_template(
            "connect.html", people=people, countries=countries, colleges=colleges
        )


@app.route("/events", methods=["GET", "POST"])
@login_required
def show_all_events():
    """Display a searchable page with all the events."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        title_query = request.form.get("title")

        # Create a search query
        query = "SELECT * FROM event WHERE (:title_query IS NULL OR title LIKE :title_query) ORDER BY date"

        # Execute the search query to display specific events
        events = db.execute(
            query, title_query=f"%{title_query}%" if title_query else None
        )

        return render_template("events.html", events=events)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # If given no specific search parameters, display all the events
        events = db.execute("SELECT * FROM event ORDER BY date")

        return render_template("events.html", events=events)


@app.route("/create_event", methods=["POST", "GET"])
@login_required
def create_event():
    """A form where the user can create an event."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        location = request.form.get("location")

        # Add event data to database
        db.execute(
            "INSERT INTO event (title, description, date, location) VALUES (?, ?, ?, ?)",
            title,
            description,
            date,
            location,
        )

        return redirect(url_for("show_all_events"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("create_event.html")


@app.route("/opportunities", methods=["GET", "POST"])
@login_required
def show_all_opportunities():
    """Display a searchable page with all the opportunities."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        title_query = request.form.get("title")

        # Create a search query
        query = "SELECT * FROM opportunity WHERE (:title_query IS NULL OR title LIKE :title_query) ORDER BY deadline"

        # Execute the search query to display specific opportunities
        opportunities = db.execute(
            query, title_query=f"%{title_query}%" if title_query else None
        )

        return render_template("opportunities.html", opportunities=opportunities)

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # If given no specific search parameters, display all the opportunities
        opportunities = db.execute("SELECT * FROM opportunity ORDER BY deadline")

        return render_template("opportunities.html", opportunities=opportunities)


@app.route("/create_opportunity", methods=["POST", "GET"])
@login_required
def create_opportunity():
    """A form where the user can create an opportunity."""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Retrieve data from form
        title = request.form.get("title")
        description = request.form.get("description")
        linked_application = request.form.get("linked_application")
        deadline = request.form.get("deadline")

        # Add opportunity data to database
        db.execute(
            "INSERT INTO opportunity (title, description, linked_application, deadline) VALUES (?, ?, ?, ?)",
            title,
            description,
            linked_application,
            deadline,
        )

        return redirect(url_for("show_all_opportunities"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("create_opportunity.html")
