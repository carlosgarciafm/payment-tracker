from flask import Flask, render_template, session, request, redirect
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from dbschema import User, Purchase, Payment, db
from utils import login_required, apology, formatter

# Application configuration.
app = Flask(__name__)

# Database configuration.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paymenttracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.app = app
db.init_app(app)
db.create_all()

# Configure custom jinja filters.
app.jinja_env.filters["formatter"] = formatter

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show a summary for the current user."""
    headers = ["purchases", "payments", "debt", "total"]

    # Query user from database.
    user = User.query.filter_by(id=session["user_id"]).first()
    profile = {"avatar_url": user.avatar_url,
               "debt": user.debt,
               "total": sum([purchase.price for purchase in user.purchases]),
               "purchases": len(user.purchases),
               "payments": len([payments for purchase in user.purchases
                                for payments in purchase.payments])}

    return render_template("index.html", headers=headers, profile=profile)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Allow the user to login using their credentials."""
    # Clear any existing user session.
    session.clear()

    if request.method == "POST":
        # Missing both username and password.
        if (not request.form.get("username") and
           not request.form.get("password")):
            return apology("both", "username and password", "why not both?")

        # Query user from database.
        user = User.query.filter_by(
                username=request.form.get("username")).first()

        # User is not in database.
        if not user:
            return apology("doge",
                           "user not found",
                           "have you registered already?",
                           code=404)

        # Wrong password.
        if not check_password_hash(user.pw_hash, request.form.get("password")):
            return apology("stop-it",
                           "stop it,",
                           "get the right password",
                           code=403)

        # Attach user to the current session.
        session["user_id"] = user.id
        session["username"] = user.username
        session["avatar_url"] = user.avatar_url

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Allow the user to logout."""
    # Clear any existing user session.
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Allow a new user to register."""
    if request.method == "POST":
        # Missing username, password and confirmation.
        if (not request.form.get("username") and
           not request.form.get("password") and
           not request.form.get("confirmation")):
            return apology("both", "username, password and confirmation",
                           "why not all?")

        # Missing either username, password or confirmation.
        if (not request.form.get("username") or
           not request.form.get("password") or
           not request.form.get("confirmation")):
            return apology("cheems", "username, password or confirmation",
                           "something's missing")

        # Query user from database.
        user = User.query.filter_by(
                username=request.form.get("username")).first()

        # User is already in database.
        if user:
            return apology("aag",
                           "username taken",
                           " ",
                           code=403)

        # Passwords do not match.
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("stop-it",
                           "stop it,",
                           "get matching password and confirmation",
                           code=403)

        # Create new user.
        user = User(username=request.form.get("username"),
                    pw_hash=generate_password_hash(
                        request.form.get("password")))

        # Add user to database.
        db.session.add(user)
        db.session.commit()

        # Attach user to the current session.
        session["user_id"] = user.id
        session["username"] = user.username
        session["avatar_url"] = user.avatar_url

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/purchase", methods=["GET", "POST"])
@login_required
def purchase():
    """Allow the user to register a new purchase."""
    status = ["Cleared", "Pending"]
    if request.method == "POST":
        required_fields = ["seller", "item", "status", "price"]
        for field in required_fields:
            # Missing data from form.
            if not request.form.get(field):
                return apology("fine", " ", f"{field} is missing")

        # Create new purchase.
        purchase = Purchase(seller=request.form.get("seller"),
                            item=request.form.get("item"),
                            description=request.form.get("description"),
                            status=request.form.get("status"),
                            price=request.form.get("price", type=float),
                            user_id=session["user_id"])

        # Invalid status.
        if purchase.status not in status:
            return apology("cheems", purchase.status, "invalid status", 400)

        # Update debt on "Pending" purchases.
        if purchase.status == "Pending":
            purchase.debt = purchase.price

            # Update user's debt.
            user = User.query.filter_by(id=purchase.user_id).first()
            user.debt += purchase.debt

        # Add purchase to database.
        db.session.add(purchase)
        db.session.commit()

        return redirect("/purchases")
    else:
        return render_template("purchase.html", status=status)


@app.route("/purchases", methods=["GET"])
@login_required
def purchases():
    """Allow the user to view cleared and pending purchases."""
    headers = ["item", "seller", "description", "price", "debt", "date"]

    # Get all pending purchases for the current user.
    pending = Purchase.query.filter_by(
            user_id=session["user_id"]).filter_by(status="Pending").order_by(
                    db.desc(Purchase.date)).all()

    # Get all cleared purchases for the current user.
    cleared = Purchase.query.filter_by(
            user_id=session["user_id"]).filter_by(status="Cleared").order_by(
                    db.desc(Purchase.date)).all()

    # Store purchases information in dictionary form: {"status": [purchases]}.
    purchases_data = {"Pending": pending, "Cleared": cleared}

    return render_template("purchases.html",
                           headers=headers,
                           purchases_data=purchases_data)


@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    """Allow the user to register a new payment on a pending purchase."""
    if request.method == "POST":
        required_fields = ["purchase_id", "amount"]
        for field in required_fields:
            # Missing data from form.
            if not request.form.get(field):
                return apology("fine", " ", f"{field} is missing")

        # Create new payment.
        payment = Payment(amount=request.form.get("amount", type=float),
                          purchase_id=request.form.get("purchase_id"),
                          user_id=session["user_id"])

        # Payment on cleared purchase.
        if not Purchase.query.filter_by(status="Pending").filter_by(
                id=payment.purchase_id).first():
            return apology("woman-cat", " ", "invalid purchase", 400)

        # Verify the purchase exists in the database.
        purchase = Purchase.query.filter_by(id=payment.purchase_id).first()
        if not purchase:
            return apology("patrick",
                           "why don't we take this payment",
                           "and apply it to an existing purchase", 400)
        # Payment amount exceeds debt.
        if payment.amount > purchase.debt:
            payment.amount = purchase.debt
        # Update purchase's debt.
        purchase.debt -= payment.amount
        # Purchase has been paid in full.
        if purchase.debt == 0:
            purchase.status = "Cleared"

        # Update user's debt.
        user = User.query.filter_by(id=Purchase.query.filter_by(
            id=payment.purchase_id).first().user_id).first()
        if not user:
            return apology("disasatergirl",
                           " ",
                           "missing user", 400)
        user.debt -= payment.amount

        # Add payment to database.
        db.session.add(payment)
        db.session.add(purchase)
        db.session.add(user)
        db.session.commit()

        return redirect("/payments")
    else:
        # Get all pending purchases for the current user.
        pending = Purchase.query.filter_by(
                user_id=session["user_id"]).filter_by(
                        status="Pending").order_by(
                                db.desc(Purchase.date)).all()

        return render_template("payment.html", pending=pending)


@app.route("/payments", methods=["GET"])
@login_required
def payments():
    """Allow the user to view all payments."""
    headers = ["amount", "date"]

    # Get all payments for the current user.
    payments = Payment.query.filter_by(user_id=session["user_id"]).order_by(
            db.desc(Payment.date)).all()

    return render_template("payments.html", headers=headers, payments=payments)
