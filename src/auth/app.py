import mysql.connector
from flask import Flask, render_template, request, redirect, url_for
import os, re
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash


app = Flask(__name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
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
                    return render_template('student.html', user=user)
                elif role == 'teacher':
                    return render_template('teacher.html', user=user)
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


if __name__ == '__main__':
    app.run(debug=True)
