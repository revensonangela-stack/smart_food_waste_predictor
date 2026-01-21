from flask import (
    Flask, request, jsonify, render_template,
    redirect, flash, url_for
)
from flask_login import (
    LoginManager, login_user, logout_user,
    login_required, current_user
)
from models import db, IngredientUsage, Ingredient, User
from collections import defaultdict
from datetime import datetime, timedelta
import os
import secrets
from functools import wraps

# -----------------------------
# App Setup
# -----------------------------
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change_this_secret")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# -----------------------------
# Flask-Login Setup
# -----------------------------
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -----------------------------
# Disable back button cache
# -----------------------------
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# -----------------------------
# Role-based decorator
# -----------------------------
def role_required(role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("login"))
            if current_user.role != role:
                flash("Unauthorized access", "danger")
                return redirect(url_for("dashboard"))
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# -----------------------------
# Create DB & Default Admin
# -----------------------------
with app.app_context():
    db.create_all()

    admin_username = os.getenv("ADMIN_USER", "admin")
    admin_password = os.getenv("ADMIN_PASS", "admin123")

    if not User.query.filter_by(username=admin_username).first():
        admin = User(
            username=admin_username,
            role="admin",
            must_reset_password=False
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()

# -----------------------------
# Helpers
# -----------------------------
def grams_to_kg(value):
    return round(value / 1000, 2)

# -----------------------------
# Authentication
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(
            username=request.form.get("username")
        ).first()

        if not user or not user.check_password(request.form.get("password")):
            flash("Invalid credentials", "danger")
            return redirect(url_for("login"))

        login_user(user)

        if user.must_reset_password:
            return redirect(url_for("reset_password"))

        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# -----------------------------
# Force Password Reset
# -----------------------------
@app.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password():
    if not current_user.must_reset_password:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if len(password) < 6:
            flash("Password must be at least 6 characters", "danger")
            return redirect(url_for("reset_password"))

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("reset_password"))

        current_user.set_password(password)
        current_user.must_reset_password = False
        db.session.commit()

        flash("Password updated successfully. Please login again.", "success")
        logout_user()
        return redirect(url_for("login"))

    return render_template("reset_password.html")

# -----------------------------
# Pages
# -----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/admin")
@login_required
@role_required("admin")
def admin_dashboard():
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    return render_template("admin.html", ingredients=ingredients)

@app.route("/add-data")
@login_required
@role_required("staff")
def add_data_page():
    return render_template("add_data.html")

# -----------------------------
# INGREDIENT MANAGEMENT (ADMIN)
# -----------------------------
@app.route("/admin/ingredients", methods=["GET"])
@login_required
@role_required("admin")
def admin_ingredients():
    return render_template("admin.html")

@app.route("/admin/ingredients/list", methods=["GET"])
@login_required
@role_required("admin")
def list_ingredients():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 8))

    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()

    query = Ingredient.query

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Ingredient.name.ilike(f"%{search}%"))

    paginated = query.order_by(Ingredient.name).paginate(page=page, per_page=per_page)

    ingredients = [
        {"id": i.id, "name": i.name, "category": i.category}
        for i in paginated.items
    ]

    return jsonify({
        "ingredients": ingredients,
        "page": paginated.page,
        "total_pages": paginated.pages,
        "total_items": paginated.total
    })

@app.route("/admin/ingredients/add", methods=["POST"])
@login_required
@role_required("admin")
def add_ingredient():
    data = request.get_json()
    name = data.get("name", "").strip()
    category = data.get("category", "").strip()

    if not name or not category:
        return jsonify({"error": "Name and category required"}), 400

    if Ingredient.query.filter_by(name=name).first():
        return jsonify({"error": "Ingredient already exists"}), 409

    ingredient = Ingredient(name=name, category=category)
    db.session.add(ingredient)
    db.session.commit()

    return jsonify({
        "message": "Ingredient added",
        "ingredient": {
            "id": ingredient.id,
            "name": ingredient.name,
            "category": ingredient.category
        }
    }), 201

@app.route("/admin/ingredients/<int:ingredient_id>", methods=["PUT"])
@login_required
@role_required("admin")
def edit_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    data = request.get_json()

    ingredient.name = data.get("name", ingredient.name).strip()
    ingredient.category = data.get("category", ingredient.category).strip()

    db.session.commit()
    return jsonify({"message": "Ingredient updated"}), 200

@app.route("/admin/ingredients/<int:ingredient_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_ingredient(ingredient_id):
    ingredient = Ingredient.query.get_or_404(ingredient_id)
    db.session.delete(ingredient)
    db.session.commit()
    return jsonify({"message": "Ingredient deleted"}), 200

@app.route("/ingredient-waste-report")
@login_required
def ingredient_waste_report():
    report = {}

    entries = IngredientUsage.query.all()

    for entry in entries:
        ingredient = entry.ingredient
        if not ingredient:
            continue

        name = ingredient.name

        if name not in report:
            report[name] = {
                "used": 0.0,
                "wasted": 0.0
            }

        report[name]["used"] += entry.used_quantity_g
        report[name]["wasted"] += entry.wasted_quantity_g

    result = []

    for name, values in report.items():
        used = values["used"]
        wasted = values["wasted"]

        waste_percentage = (wasted / used) * 100 if used > 0 else 0

        result.append({
            "ingredient": name,
            "waste_percentage": round(waste_percentage, 2)
        })

    return jsonify(result)



# -----------------------------
# INGREDIENT USAGE (STAFF)
# -----------------------------
@app.route("/add", methods=["POST"])
@login_required
@role_required("staff")
def add_ingredient_usage():
    data = request.get_json()

    ingredient_id = data.get("ingredient_id")
    used_quantity = data.get("used_quantity")
    wasted_quantity = data.get("wasted_quantity")
    unit = data.get("unit")
    entry_date = data.get("entry_date")

    if not all([ingredient_id, used_quantity is not None, wasted_quantity is not None, unit, entry_date]):
        return jsonify({"error": "Missing required fields"}), 400

    # Normalize to grams
    if unit == "kg":
        used_g = used_quantity * 1000
        wasted_g = wasted_quantity * 1000
    elif unit == "g":
        used_g = used_quantity
        wasted_g = wasted_quantity
    elif unit == "pcs":
        # Simple assumption: 1 piece = 100g (you can improve later)
        used_g = used_quantity * 100
        wasted_g = wasted_quantity * 100
    else:
        return jsonify({"error": "Invalid unit"}), 400

    usage = IngredientUsage(
        ingredient_id=ingredient_id,
        used_quantity=used_quantity,
        wasted_quantity=wasted_quantity,
        unit=unit,
        used_quantity_g=used_g,
        wasted_quantity_g=wasted_g,
        entry_date=datetime.strptime(entry_date, "%Y-%m-%d").date()
    )

    db.session.add(usage)
    db.session.commit()

    return jsonify({"message": "Usage data saved successfully"}), 201

@app.route("/ingredients", methods=["GET"])
@login_required
def get_ingredients():
    ingredients = Ingredient.query.order_by(Ingredient.name).all()
    return jsonify([{"id": i.id, "name": i.name} for i in ingredients])


# -----------------------------
# Manage Staff (ADMIN)
# -----------------------------

@app.route("/admin/manage-staff")
@login_required
@role_required("admin")
def manage_staff():
    staff_list = User.query.filter_by(role="staff").all()
    return render_template("manage_staff.html", staff_list=staff_list)

@app.route("/admin/staff/add", methods=["POST"])
@login_required
@role_required("admin")
def add_staff():
    username = request.form.get("username", "").strip()

    if not username:
        flash("Username is required", "danger")
        return redirect(url_for("manage_staff"))

    if User.query.filter_by(username=username).first():
        flash("Staff user already exists", "warning")
        return redirect(url_for("manage_staff"))

    temp_password = secrets.token_urlsafe(8)

    staff = User(username=username, role="staff", must_reset_password=True)
    staff.set_password(temp_password)

    db.session.add(staff)
    db.session.commit()

    flash(f"Staff created. Temporary password: {temp_password}", "success")
    return redirect(url_for("manage_staff"))

@app.route("/admin/staff/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_staff(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        flash("Admin cannot be deleted", "danger")
        return redirect(url_for("manage_staff"))

    db.session.delete(user)
    db.session.commit()
    flash("Staff deleted", "success")
    return redirect(url_for("manage_staff"))

@app.route("/admin/staff/<int:user_id>/edit", methods=["POST"])
@login_required
@role_required("admin")
def edit_staff(user_id):
    user = User.query.get_or_404(user_id)
    new_username = request.form.get("username", "").strip()

    if not new_username:
        flash("Username required", "danger")
        return redirect(url_for("manage_staff"))

    user.username = new_username
    db.session.commit()
    flash("Staff updated", "success")
    return redirect(url_for("manage_staff"))

@app.route("/admin/staff/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required("admin")
def reset_staff_password(user_id):
    user = User.query.get_or_404(user_id)
    temp_password = secrets.token_urlsafe(8)

    user.set_password(temp_password)
    user.must_reset_password = True
    db.session.commit()

    flash(f"Temporary password: {temp_password}", "success")
    return redirect(url_for("manage_staff"))

# -----------------------------
# Dashboard APIs
# -----------------------------
@app.route("/dashboard-data")
@login_required
def dashboard_data():
    entries = IngredientUsage.query.all()
    return jsonify({
        "total_used": grams_to_kg(sum(e.used_quantity_g for e in entries)),
        "total_wasted": grams_to_kg(sum(e.wasted_quantity_g for e in entries)),
        "unit": "kg"
    })

@app.route("/daily-summary")
@login_required
def daily_summary():
    daily = defaultdict(lambda: {"used_g": 0, "wasted_g": 0})

    for e in IngredientUsage.query.all():
        day = e.entry_date.strftime("%Y-%m-%d")
        daily[day]["used_g"] += e.used_quantity_g
        daily[day]["wasted_g"] += e.wasted_quantity_g

    return jsonify({
        d: {
            "total_used": grams_to_kg(v["used_g"]),
            "total_wasted": grams_to_kg(v["wasted_g"])
        } for d, v in sorted(daily.items())
    })

# -----------------------------
# WEEKLY RECOMMENDATIONS
# -----------------------------
@app.route("/weekly-recommendations")
@login_required
def weekly_recommendations():
    today = datetime.now().date()
    last_week_start = today - timedelta(days=7)
    prev_week_start = today - timedelta(days=14)

    last_week = defaultdict(int)
    prev_week = defaultdict(int)

    for entry in IngredientUsage.query.all():
        entry_date = entry.entry_date  # ✅ FIXED HERE

        if last_week_start <= entry_date <= today:
            last_week[entry.ingredient_id] += entry.wasted_quantity_g

        elif prev_week_start <= entry_date < last_week_start:
            prev_week[entry.ingredient_id] += entry.wasted_quantity_g

    recommendations = []

    for ingredient_id, wasted_g in last_week.items():
        prev_wasted_g = prev_week.get(ingredient_id, 0)

        ingredient = Ingredient.query.get(ingredient_id)
        name = ingredient.name if ingredient else "Unknown"

        if wasted_g > prev_wasted_g * 1.2:
            recommendations.append({
                "type": "Reduce",
                "message": (
                    f"Waste for {name} increased this week. "
                    f"Consider buying less or improving storage."
                )
            })

        elif prev_wasted_g > 0 and wasted_g < prev_wasted_g * 0.8:
            recommendations.append({
                "type": "Good",
                "message": (
                    f"Great job! Waste for {name} decreased. "
                    f"Keep up the good habits."
                )
            })

    if not recommendations:
        recommendations.append({
            "type": "Info",
            "message": "No major waste changes this week. Keep tracking usage!"
        })

    return jsonify({"recommendations": recommendations})


# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
