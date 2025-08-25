import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "change-me-please")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(BASE_DIR, "wfa.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "admin_login"

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # "piese" or "detailing"
    price = db.Column(db.Float, nullable=False, default=0.0)
    description = db.Column(db.Text, nullable=True)
    image_filename = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

@app.cli.command("init-db")
def init_db():
    "Initialize database and create default admin if not exists"
    db.create_all()
    if not Admin.query.filter_by(username="wfa_admin").first():
        from getpass import getpass
        default_pass = os.environ.get("WFA_DEFAULT_PASS", "WFA#Garage2025")
        admin = Admin(username="wfa_admin")
        admin.set_password(default_pass)
        db.session.add(admin)
        db.session.commit()
        print("Created default admin: wfa_admin /", default_pass)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/produse")
def produse():
    cat = request.args.get("cat")
    query = Product.query.order_by(Product.created_at.desc())
    if cat in ("piese", "detailing"):
        query = query.filter_by(category=cat)
    items = query.all()
    return render_template("produse.html", items=items, cat=cat)

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Admin routes
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = Admin.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Autentificare reușită.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Date de logare invalide.", "danger")
    return render_template("admin_login.html")

@app.route("/admin/logout")
@login_required
def admin_logout():
    logout_user()
    flash("Delogat.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin_dashboard.html", items=items)

@app.route("/admin/add", methods=["GET", "POST"])
@login_required
def admin_add():
    if request.method == "POST":
        name = request.form.get("name")
        category = request.form.get("category")
        price = float(request.form.get("price") or 0)
        description = request.form.get("description")
        image = request.files.get("image")
        filename = None
        if image and image.filename:
            filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + image.filename.replace(" ", "_")
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        prod = Product(name=name, category=category, price=price, description=description, image_filename=filename)
        db.session.add(prod)
        db.session.commit()
        flash("Produs adăugat.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_add.html")

@app.route("/admin/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def admin_edit(pid):
    prod = Product.query.get_or_404(pid)
    if request.method == "POST":
        prod.name = request.form.get("name")
        prod.category = request.form.get("category")
        prod.price = float(request.form.get("price") or 0)
        prod.description = request.form.get("description")
        image = request.files.get("image")
        if image and image.filename:
            filename = datetime.utcnow().strftime("%Y%m%d%H%M%S_") + image.filename.replace(" ", "_")
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            prod.image_filename = filename
        db.session.commit()
        flash("Produs actualizat.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_edit.html", item=prod)

@app.route("/admin/delete/<int:pid>", methods=["POST"])
@login_required
def admin_delete(pid):
    prod = Product.query.get_or_404(pid)
    db.session.delete(prod)
    db.session.commit()
    flash("Produs șters.", "warning")
    return redirect(url_for("admin_dashboard"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
