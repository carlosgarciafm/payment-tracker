from flask import Flask, render_template, session
from flask_session import Session
from tempfile import mkdtemp
from dbschema import User, Purchase, Payment, db
from utils import login_required

# Application configuration.
app = Flask(__name__)

# Database configuration.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paymenttracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)
db.create_all()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@login_required
def index():
    return render_template("index.html")
