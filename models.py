from datetime import date
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# -----------------------------
# Ingredient Models
# -----------------------------
class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    category = db.Column(
        db.String(50),
        nullable=False
    )

    def __repr__(self):
        return f"<Ingredient {self.name} ({self.category})>"

class IngredientUsage(db.Model):
    __tablename__ = "ingredient_usages"

    id = db.Column(db.Integer, primary_key=True)

    ingredient_id = db.Column(
        db.Integer,
        db.ForeignKey("ingredients.id"),
        nullable=False
    )

    ingredient = db.relationship(
        "Ingredient",
        backref="usages"
    )

    # Original input values
    used_quantity = db.Column(db.Float, nullable=False)
    wasted_quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(10), nullable=False)

    # Normalized values (grams)
    used_quantity_g = db.Column(db.Float, nullable=False)
    wasted_quantity_g = db.Column(db.Float, nullable=False)

    entry_date = db.Column(
        db.Date,
        default=date.today,
        nullable=False
    )

    def waste_percentage(self):
        if self.used_quantity_g == 0:
            return 0
        return (self.wasted_quantity_g / self.used_quantity_g) * 100

# -----------------------------
# User Model
# -----------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )  # admin / staff

    must_reset_password = db.Column(
        db.Boolean,
        default=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
