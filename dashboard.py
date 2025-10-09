from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this in production!

login_manager = LoginManager()
login_manager.init_app(app)

# Dummy user store
class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.name = "admin"
        self.password = "password"  # Change this in production!

users = {"admin": User("admin")}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "admin" and request.form['password'] == "password":
            user = users["admin"]
            login_user(user)
            return redirect(url_for('index'))
        return "Invalid credentials", 401
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Existing index route ---
@app.route('/')
@login_required
def index():
    # Load printer info
    try:
        with open('printers.json') as f:
            printers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        printers = []

    # Load last known states
    try:
        with open('states.json') as f:
            states = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        states = {}

    # Combine data with validation
    for p in printers:
        if isinstance(p, dict) and "name" in p and "ip" in p:
            p["status"] = states.get(p["ip"], "unknown")
        else:
            p["status"] = "invalid"

    last_checked = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template('index.html', printers=printers, last_checked=last_checked, current_user=current_user)

# --- REST API endpoint ---
@app.route('/api/printers')
@login_required
def api_printers():
    try:
        with open('printers.json') as f:
            printers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        printers = []

    try:
        with open('states.json') as f:
            states = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        states = {}

    for p in printers:
        if isinstance(p, dict) and "name" in p and "ip" in p:
            p["status"] = states.get(p["ip"], "unknown")
        else:
            p["status"] = "invalid"

    return jsonify(printers)

# --- Printer details/history ---
@app.route('/printer/<ip>')
@login_required
def printer_details(ip):
    try:
        with open('printers.json') as f:
            printers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        printers = []

    printer = next((p for p in printers if p.get("ip") == ip), None)
    if not printer:
        return "Printer not found", 404

    # Load history (example: from printer_history.json)
    try:
        with open('printer_history.json') as f:
            history = json.load(f).get(ip, [])
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    return render_template('printer_details.html', printer=printer, history=history)

if __name__ == '__main__':
    # Set debug=False for production
    app.run(host='0.0.0.0', port=5000, debug=False)
