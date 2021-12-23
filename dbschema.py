from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


# Declare database without intitialising it.
db = SQLAlchemy()


class User(db.Model):
    """Create User schema."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    pw_hash = db.Column(db.String, nullable=False)
    avatar_url = db.Column(db.String, nullable=True)

    # Declare one-to-many relationship with purchases table.
    purchases = db.relationship("Purchase", backref=db.backref("user", lazy=True))

    def __repr__(self):
        return "<User %r>" % self.id


class Purchase(db.Model):
    """Create Purchase schema."""
    __tablename__ = "purchases"
    id = db.Column(db.Integer, primary_key=True)
    seller = db.Column(db.String(40), nullable=False)
    item = db.Column(db.String(40), nullable=False)
    description = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    debt = db.Column(db.Float, nullable=False, default=0.0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Add reference to user.id within purchases table.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    # Declare one-to-many relationship with payments table.
    payments = db.relationship("Payment", backref=db.backref("purchase", lazy=True))

    def __repr__(self):
        return "<Purchase %r>" % self.id


class Payment(db.Model):
    """Create Payment schema."""
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Add reference to puchase.id within payments table.
    purchase_id = db.Column(db.Integer, db.ForeignKey("purchases.id"), nullable=False)

    def __repr__(self):
        return "<Payment %r>" % self.id
