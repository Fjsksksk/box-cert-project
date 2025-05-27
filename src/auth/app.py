import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
import os, re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import json
import os
import sys

# ajouter le dossier src au sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from algo import load_students_from_file, group_students, save_groups

app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
)

# Fonction pour connecter à la base de données
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='W@2915djkq#',
        database='vote_user'
    )
# Route pour la connexion
@app.route('/auth/signin', methods=['GET', 'POST'])
def signin():
    errors = {}

    if request.method == 'POST':
        identifier = request.form.get('first_name', '').strip()
        password = request.form.get('password', '').strip()

        # Check if identifier is in the format lastname.firstname
        if '.' in identifier:
            last_name, first_name = identifier.split('.', 1)
        else:
            errors['general'] = "Invalid identifier format. Expected: lastname.firstname"
            return render_template('auth/signin.html', errors=errors, request=request)

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT * FROM users WHERE firstname = %s AND lastname = %s
            """
            cursor.execute(query, (first_name, last_name))  
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        
            if user and check_password_hash(user['password_user'], password):
                role = user['role']
                if role == 'student':
                    return redirect(url_for('student'))
                elif role == 'teacher':
                    return redirect(url_for('teacher'))
                else:
                    errors['general'] = "Unknown role."
            else:
                errors['general'] = "Incorrect identifier or password."
        except Exception as e:
            errors['general'] = f"Connection error: {str(e)}"

    return render_template('auth/signin.html', errors=errors, request=request)


@app.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    errors = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        family_name = request.form.get('family_name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        admin_code = request.form.get('admin_code', '').strip()

        # Validation du mot de passe
        if len(password) < 8:
            errors['password'] = "Password must contain at least 8 characters."
        elif len(re.findall(r"\d", password)) < 2:
            errors['password'] = "Password must contain at least 2 digits."
        elif not re.search(r"[A-Za-z]", password):
            errors['password'] = "Password must contain at least one letter."

        if password != confirm_password:
            errors['confirm_password'] = "Passwords are not compatible."

        # Détermination du rôle
        role = 'student'  # valeur par défaut
        if admin_code:
            if admin_code == '123':
                role = 'teacher'
            else:
                errors['admin_code'] = "Admin code invalide."

        # Si tout est valide, insérer dans la base
     # Si tout est valide, insérer dans la base
        if not errors:
            try:
                hashed_password = generate_password_hash(password)

                conn = get_db_connection()
                cursor = conn.cursor()
                query = """
                    INSERT INTO users (firstname, lastname, password_user, role)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (first_name, family_name, hashed_password, role))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('signin'))
            except Exception as e:
                errors['general'] = f"Erreur lors de l'inscription : {str(e)}"


    return render_template('auth/signup.html', errors=errors, request=request)


# Redirection vers la page de connexion par défaut
@app.route('/')
def index():
    return render_template('index.html')


app.secret_key = "secret"  # Requis pour flash()

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
PREFERENCES_FILE = os.path.join(DATA_DIR, "preferences.json")
GROUP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/group.json"))
CHOICES_FILE=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/choice.json"))
def load_preferences():
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"num_preferences": 3}

def save_preferences(num):
    os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump({"num_preferences": num}, f, ensure_ascii=False, indent=2)

@app.route('/teacher', methods=["GET", "POST"])
def teacher():
    num_preferences = load_preferences()["num_preferences"]
    groups = []
    show_confirm_buttons = False

    if request.method == "POST":
        if 'num_preferences' in request.form:
            num_preferences = int(request.form["num_preferences"])
            save_preferences(num_preferences)
            flash("Nombre d'affinités enregistré.", "success")
            return redirect(url_for("teacher"))

        elif 'generate_groups' in request.form or 'confirm_generation' in request.form:
            try:
                group_size = int(request.form["group_size"])
                students = load_students_from_file(CHOICES_FILE)
                total_students = len(students)

                # Si incompatibilité détectée et pas de confirmation
                if total_students % group_size != 0 and 'confirm_generation' not in request.form:
                    flash(f"Incompatibilité : {total_students} étudiants ne peuvent pas être divisés en groupes de {group_size}.", "warning")
                    flash("Souhaitez-vous générer quand même ?", "info")
                    show_confirm_buttons = True  # pour afficher les boutons
                else:
                    groups = group_students(students, group_size, num_preferences)
                    if groups:
                        save_groups(groups)
                        flash("Groupes générés avec succès.", "success")
                    else:
                        flash("Impossible de générer les groupes. Essayez un autre nombre.", "danger")
            except Exception as e:
                flash(f"Erreur : {str(e)}", "danger")

    # Charger groupes existants si présents
    if os.path.exists(GROUP_FILE):
        try:
            with open(GROUP_FILE, "r", encoding="utf-8") as f:
                groups = json.load(f)
        except:
            groups = []

    return render_template("teacher.html", num_preferences=num_preferences, groups=groups, show_confirm_buttons=show_confirm_buttons)
if __name__ == '__main__':
    app.run(debug=True)
