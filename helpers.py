from flask import render_template, redirect, session
from functools import wraps
import re
from cs50 import SQL
from datetime import datetime
import base64


db = SQL("sqlite:///bridge.db")


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return (
        render_template(
            "apology.html", message=message, top=code, bottom=escape(message)
        ),
        code,
    )


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def is_strong_password(password):
    """Check if user's password meets the requirements."""

    # Define the regular expression pattern
    pattern = (
        r"^(?=.*[a-z])"  # At least one lowercase letter
        r"(?=.*[A-Z])"  # At least one uppercase letter
        r"(?=.*\d)"  # At least one digit
        r"(?=.*[@$!%*?&])"  # At least one special character
        r"[A-Za-z\d@$!%*?&]{8,}$"  # Minimum length of 8 characters
    )

    # Check if given password matches the pattern
    match_result = re.fullmatch(pattern, password)
    is_strong = match_result is not None

    return is_strong


def get_username(user_id):
    """Retrieve username of given user id to format the post in feed."""

    # Query database for user
    user_data = db.execute("SELECT * FROM user WHERE id = ?", user_id)

    # If the user exists, return their username
    if user_data:
        return f"{user_data[0]['username']}"

    # Otherwise, return unknown user
    else:
        return "Unknown User"


def get_like_count(post_id):
    """Retrieve number of likes of given post id to format the post in feed."""

    # Query database for number of likes on the post
    like_count = db.execute(
        "SELECT COUNT(*) FROM post_like WHERE post_id = ?", post_id
    )[0]

    return like_count


def get_comments(post_id):
    """Retrieve comments of given post id to format the post in feed."""

    # Query database for the comments under the post
    comments = db.execute(
        "SELECT content, user_id, created_at FROM post_comment WHERE post_id = ?",
        post_id,
    )

    # Format the comments in a readable way
    formatted_comments = []

    for comment in comments:
        user_name = get_username(comment["user_id"])
        formatted_comment = {
            "user_name": user_name,
            "content": comment["content"],
            "time": comment["created_at"],
        }
        formatted_comments.append(formatted_comment)

    return formatted_comments


def get_formatted_date(created_at):
    """Retrieve the current date in a nice format."""

    # Get the current date
    datetime_object = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")

    # Format the date
    formatted_date = datetime_object.strftime("%B %d, %Y")

    return formatted_date


def get_user_profile(user_id):
    """Retrieve all of the user's data in a readable format."""

    # Query databse for user's data from the user, profile_questions, and socials tables
    user_data = db.execute(
        "SELECT username, fname, lname, image, email, bio, location, country_id, college_id FROM user WHERE id = ?",
        user_id,
    )[0]
    answers = db.execute(
        "SELECT answer1, answer2, answer3 FROM profile_questions WHERE user_id = ?",
        user_id,
    )[0]
    socials = db.execute(
        "SELECT instagram, facebook, linkedin FROM socials WHERE user_id = ?", user_id
    )[0]

    # Create a dictionary with each data point for the user
    user_dict = {
        "username": user_data["username"],
        "fname": user_data["fname"],
        "lname": user_data["lname"],
        "email": user_data["email"],
        "image": user_data["image"],
        "bio": user_data["bio"],
        "location": user_data["location"],
        "country": db.execute(
            "SELECT name FROM country WHERE id = ?", user_data["country_id"]
        )[0]["name"],
        "college": db.execute(
            "SELECT name FROM college WHERE id = ?", user_data["college_id"]
        )[0]["name"],
        "answer1": answers["answer1"],
        "answer2": answers["answer2"],
        "answer3": answers["answer3"],
        "instagram": socials["instagram"],
        "facebook": socials["facebook"],
        "linkedin": socials["linkedin"],
    }

    return user_dict


def update_data_image(user_data):
    """Add a user's profile picture to the dictionary with their data."""

    # If a user has no image, use a placeholder instead
    if user_data["image"] == None:
        user_data[
            "image_url"
        ] = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/User-avatar.svg/1200px-User-avatar.svg.png"

    # Otherwise update the user's image to the one they uploaded
    else:
        user_data["image_url"] = "data:image/png;base64," + base64.b64encode(
            user_data["image"]
        ).decode("utf-8")

    return user_data
