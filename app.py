from flask import Flask, render_template
from dbschema import User, Purchase, Payment, db

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paymenttracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)
db.create_all()

@app.route("/")
def index():
    return render_template("index.html")
