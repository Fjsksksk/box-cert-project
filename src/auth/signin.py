
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
)

# Simule une base de données d’utilisateurs pour la démo
USERS = {
    'Jean': 'motdepasse123',
    'Marie': 'azerty'
}

@app.route('/auth/signin', methods=['GET', 'POST'])
def signin():
    errors = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        password = request.form.get('password', '').strip()

        # Vérifie si le prénom et le mot de passe correspondent
        if first_name in USERS and USERS[first_name] == password:
            return f"Bienvenue {first_name} !"
        else:
            errors['general'] = "Identifiants invalides."

    return render_template('auth/signin.html', errors=errors, request=request)

if __name__ == '__main__':
    app.run(debug=True)
