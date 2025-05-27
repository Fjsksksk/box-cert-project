import re
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates')
)

@app.route('/auth/signup', methods=['GET', 'POST'])
def signup():
    errors = {}

    if request.method == 'POST':
        first_name = request.form.get('first_name', '')
        family_name = request.form.get('family_name', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(password) < 8:
            errors['password'] = "Password must contain at least 8 characters."
        elif len(re.findall(r"\d", password)) < 2:
            errors['password'] = "Password must contain at least 2 digits."
        elif not re.search(r"[A-Za-z]", password):
            errors['password'] = "Password must contain at least one letter."

        if password != confirm_password:
            errors['confirm_password'] = "Password are not compatible."

        if not errors:
            return redirect(url_for('signup'))  # temporairement pour pas casser

    return render_template('auth/signup.html', errors=errors)

if __name__ == "__main__":
    app.run(debug=True)
