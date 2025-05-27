from flask import (
    Flask, render_template, request,
    redirect, url_for, flash
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user
from werkzeug.security import check_password_hash

# ──────────────────── basic setup ────────────────────
app = Flask(__name__)
app.config["SECRET_KEY"] = "CHANGE-ME-32-CHAR"

login_mgr = LoginManager(app)
login_mgr.login_view = "login"              # redirect if not logged in

# Dummy in-memory “user” — replace by your SQLAlchemy query
FAKE_USER = {
    "id": 1,
    "firstname": "John",
    "lastname": "Doe",
    "password_hash": "pbkdf2:sha256:260000$…",  # generate_password_hash("pass")
    "role": "student"
}

class User(UserMixin):
    """Tiny wrapper so Flask-Login is happy."""
    def __init__(self, record: dict):
        self.id = record["id"]
        self.firstname = record["firstname"]
        self.lastname = record["lastname"]
        self.role = record["role"]
        self.password_hash = record["password_hash"]

@login_mgr.user_loader
def load_user(user_id):
    # real impl: return User.query.get(user_id)
    if str(user_id) == "1":
        return User(FAKE_USER)

# ───────────────────── form (Flask-WTF) ─────────────────────
class LoginForm(FlaskForm):
    firstname     = StringField("firstname", validators=[DataRequired()])
    lastname      = StringField("lastname",  validators=[DataRequired()])
    password_user = PasswordField("password_user", validators=[DataRequired()])

# ───────────────────── route /signin ─────────────────────
@app.route("/signin", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # replace with SQLAlchemy query filtering FIRST + LAST name
        if (form.firstname.data == FAKE_USER["firstname"]
                and form.lastname.data == FAKE_USER["lastname"]
                and check_password_hash(
                        FAKE_USER["password_hash"],
                        form.password_user.data)):
            login_user(User(FAKE_USER))
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")          # will appear in template
    return render_template("auth/signin.html", form=form)

# ───────────────────── demo dashboard ─────────────────────
@app.route("/dashboard")
def dashboard():
    return "<h2>Welcome – you’re logged in!</h2>"

if __name__ == "__main__":
    app.run(debug=True)
