from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime


# CS50's function to require a login.
def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Extended version of CS50's apology function.
def apology(meme, top, bottom, code=400):
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html",
                           meme=meme,
                           top=escape(top),
                           bottom=escape(bottom),
                           code=code), code


# Format input based in it's data type. Meant to be as custom jinja filter.
def formatter(data):
    if type(data) is float:
        return "${:.2f}".format(data)
    elif type(data) is datetime:
        return data.replace(microsecond=0)
    else:
        return data
