import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash
import os, re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import json
import os
import sys
from flask import session


# Include the parent folder to access the 'algo' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from algo import load_students_from_file, group_students, save_groups

# Initialize Flask app with custom folders for templates and static files
app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)

# Establish connection to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='W@2915djkq#',
        database='vote_user'
    )



# Sign-in route (login form + logic)
@app.route('/auth/signin', methods=['GET', 'POST'])
def signin():
    errors = {}

    if request.method == 'POST':
        identifier = request.form.get('first_name', '').strip()
        password = request.form.get('password', '').strip()

        # Validate identifier format (lastname.firstname)
        if '.' in identifier:
            last_name, first_name = identifier.split('.', 1)
        else:
            errors['general'] = "Invalid identifier format. Expected: lastname.firstname"
            return render_template('auth/signin.html', errors=errors, request=request)
        
        # Look up the user in the database
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
        
            # If user is found and password matches
            if user and check_password_hash(user['password_user'], password):
                session['user'] = {
                        "firstname": user["firstname"],
                        "lastname": user["lastname"],
                        "role": user["role"]
                }
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



# Sign-up route (registration form + validation + insertion)
@app.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    
    errors = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        family_name = request.form.get('family_name', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        admin_code = request.form.get('admin_code', '').strip()

        # Password validation rules
        if len(password) < 8:
            errors['password'] = "Password must contain at least 8 characters."
        elif len(re.findall(r"\d", password)) < 2:
            errors['password'] = "Password must contain at least 2 digits."
        elif not re.search(r"[A-Za-z]", password):
            errors['password'] = "Password must contain at least one letter."

        if password != confirm_password:
            errors['confirm_password'] = "Passwords are not compatible."

        # Assign user role based on admin code
        role = 'student'
        if admin_code:
            if admin_code == '123':
                role = 'teacher'
            else:
                errors['admin_code'] = "Admin code invalide."

        # Check if user already exists before insertion
        if not errors:
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)

                
                query_check = """
                    SELECT * FROM users WHERE firstname = %s AND lastname = %s
                """
                cursor.execute(query_check, (first_name, family_name))
                existing_user = cursor.fetchone()

                if existing_user:
                    print('hello')
                    flash("Un compte avec ce prénom et nom existe déjà.","error")
                else:
                  
                    hashed_password = generate_password_hash(password)

                    query_insert = """
                        INSERT INTO users (firstname, lastname, password_user, role)
                        VALUES (%s, %s, %s, %s)
                    """
                    cursor = conn.cursor()  # repasser en mode normal si nécessaire
                    cursor.execute(query_insert, (first_name, family_name, hashed_password, role))
                    conn.commit()
                    return redirect(url_for('signin'))

                cursor.close()
                conn.close()

            except Exception as e:
                errors['general'] = f"Erreur lors de l'inscription : {str(e)}"

    return render_template('auth/signup.html', errors=errors, request=request)




# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# Session secret key
app.secret_key = "secret"

# File paths for preferences and group data
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'data'))
PREFERENCES_FILE = os.path.join(DATA_DIR, "preferences.json")
GROUP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/group.json"))
CHOICES_FILE=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/choice.json"))


def load_preferences():
    # Load current preference settings (number of preferences, vote state)
    if os.path.exists(PREFERENCES_FILE):
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"num_preferences": 3, "vote_open": False} 

def save_num_preferences(num):
    # Save number of preferences allowed
    prefs = load_preferences()
    prefs["num_preferences"] = num
    os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)

def save_vote_open(state):
    # Save vote open/close state
    prefs = load_preferences()
    prefs["vote_open"] = state
    os.makedirs(os.path.dirname(PREFERENCES_FILE), exist_ok=True)
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, ensure_ascii=False, indent=2)


def delete_student_from_choices(file_path, student_name):
    # Delete a student and remove their name from others' preferences
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for entry in data:
        entry["preferences"] = [pref for pref in entry["preferences"] if pref[0] != student_name]

    data = [entry for entry in data if entry["name"] != student_name]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return True



@app.route('/teacher', methods=["GET", "POST"])
def teacher():
    # Teacher dashboard: group generation, student management, vote control
    preferences = load_preferences()
    num_preferences = preferences["num_preferences"]
    groups = []
    show_confirm_buttons = False

    if request.method == "POST":
        # Update number of preferences
        if 'num_preferences' in request.form:
            num_preferences = int(request.form["num_preferences"])
            save_num_preferences(num_preferences)
            flash("Nombre d'affinités enregistré.", "success")
            return redirect(url_for("teacher"))

        # Generate groups (with or without confirmation)
        elif 'generate_groups' in request.form or 'confirm_generation' in request.form:
            try:
                group_size = int(request.form["group_size"])
                students = load_students_from_file(CHOICES_FILE)
                total_students = len(students)

                if total_students % group_size != 0 and 'confirm_generation' not in request.form:
                    flash(f"Incompatibilité : {total_students} étudiants ne peuvent pas être divisés en groupes de {group_size}.", "warning")
                    flash("Souhaitez-vous générer quand même ?", "info")
                    show_confirm_buttons = True
                else:
                    groups, group_scores, total_score = group_students(students, group_size)
                    if groups:
                        save_groups(groups, group_scores)
                        flash("Groupes générés avec succès.", "success")
                    else:
                        flash("Impossible de générer les groupes. Essayez un autre nombre.", "danger")
            except Exception as e:
                flash(f"Erreur : {str(e)}", "danger")

        # Open or close voting
        elif "vote_action" in request.form:
            action = request.form["vote_action"]
            preferences["vote_open"] = (action == "open")
            save_vote_open(action == "open")
            status = "ouvert" if action == "open" else "fermé"
            flash(f"Le vote a été {status}.", "info")

        # Delete a student from preferences
        elif 'delete_student' in request.form:
            student_to_delete = request.form.get("student_to_delete")
            if student_to_delete:
                success = delete_student_from_choices(CHOICES_FILE, student_to_delete)
                if success:
                    flash(f"{student_to_delete} a été supprimé avec succès.", "success")
                else:
                    flash("Erreur lors de la suppression.", "danger")
            return redirect(url_for("teacher"))
        
        # Delete all groups
        elif 'delete_groups' in request.form:
            try:
                with open(GROUP_FILE, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                flash("Tous les groupes ont été supprimés.", "success")
            except Exception as e:
                flash(f"Erreur lors de la suppression des groupes : {str(e)}", "danger")
            return redirect(url_for("teacher"))


    # Load groups and student list
    if os.path.exists(GROUP_FILE):
        try:
            with open(GROUP_FILE, "r", encoding="utf-8") as f:
                groups = json.load(f)
        except:
            groups = []

    all_students = []
    if os.path.exists(CHOICES_FILE):
        with open(CHOICES_FILE, "r", encoding="utf-8") as f:
            try:
                all_students = [entry["name"] for entry in json.load(f)]
            except:
                pass

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT CONCAT(lastname, ' ', firstname) AS full_name
        FROM users
        WHERE role = 'student'
    """)
    students_in_db = [row["full_name"].strip().lower() for row in cursor.fetchall()]
    total_students = len(students_in_db)
    voted_students = 0

    if os.path.exists(CHOICES_FILE):
        with open(CHOICES_FILE, "r", encoding="utf-8") as f:
            try:
                choices_data = json.load(f)
                for entry in choices_data:
                    name = entry.get("name", "").strip().lower()
                    preferences = entry.get("preferences", [])
                    if name in students_in_db and preferences:
                        voted_students += 1
            except json.JSONDecodeError:
                pass

    return render_template(
        "teacher.html",
        num_preferences=num_preferences,
        groups=groups,
        show_confirm_buttons=show_confirm_buttons,
        all_students=all_students,
        voted_students=voted_students,
        total_students=total_students
    )


    



@app.route('/student', methods=['GET', 'POST'])
def student():
    # Student dashboard: submit preferences
    preferences = load_preferences()

    if request.method == "POST":
        student_name = request.form.get("student_name").strip()
        selected_choices = request.form.getlist("choices")
        weights = request.form.getlist("weights")
        
        # Validate input
        try:
            weights = [int(w) for w in weights]
        except ValueError:
            flash("Les poids doivent être des nombres valides.", "danger")
            return redirect(url_for("student"))

        if len(set(selected_choices)) != len(selected_choices):
            flash("Chaque étudiant ne peut être choisi qu'une seule fois.", "danger")
            return redirect(url_for("student"))

        if sum(weights) > 100:
            flash("La somme des poids ne doit pas dépasser 100.", "danger")
            return redirect(url_for("student"))


        # Format preferences for saving
        preferences_list = [[name, weight] for name, weight in zip(selected_choices, weights)]

        # Load or initialize preferences file
        if os.path.exists(CHOICES_FILE):
            with open(CHOICES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        # Update or add new student preference entry
        updated = False
        for entry in data:
            if entry["name"] == student_name:
                entry["preferences"] = preferences_list
                updated = True
                break

        if not updated:
            data.append({
                "name": student_name,
                "preferences": preferences_list
            })

        os.makedirs(os.path.dirname(CHOICES_FILE), exist_ok=True)
        with open(CHOICES_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        flash("Vos préférences ont bien été enregistrées ou mises à jour.", "success")
        return redirect(url_for("student"))

    # Load list of other students (excluding self)
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT CONCAT(lastname, ' ', firstname) AS full_name
            FROM users
            WHERE role = 'student'
        """)
        students = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
    except Exception as e:
        flash(f"Erreur de chargement des étudiants : {str(e)}", "danger")
        students = []

    user = session.get("user")
    full_name = f"{user['lastname']} {user['firstname']}"
    students = [s for s in students if s != full_name]

    return render_template("student.html",
                           other_students=students,
                           user=user,
                           vote_open=preferences.get("vote_open", False))




@app.route('/get_group', methods=['POST'])
def get_group():
    # Route to retrieve the group of a specific student
    student_name = request.form.get("student_name").strip()
    try:
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            groups = json.load(f)

        found_group = None
        for group in groups:
            if student_name in group["groupe"]:
                found_group = group
                break

        if found_group:
            # Exclure le nom de l'étudiant lui-même
            others_in_group = [member for member in found_group["groupe"] if member.strip().lower() != student_name.strip().lower()]
            
            if others_in_group:
                group_str = ", ".join(others_in_group)
                flash(f"Vous êtes dans le groupe avec : {group_str} (Score : {found_group['score']})", "info")
            else:
                flash("Vous êtes seul dans ce groupe.", "info")
        else:
            flash("Vous n'êtes assigné à aucun groupe pour le moment.", "info")
                
    except Exception as e:
        flash(f"Erreur lors de la lecture des groupes : {str(e)}", "danger")

    return redirect(url_for("student"))




if __name__ == '__main__':
    # Start the app in debug mode
    app.run(debug=True)

 

    


    



