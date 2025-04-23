from flask import Flask, request, render_template, redirect, session, url_for
import os


app = Flask(__name__)
app.secret_key = "secret123"  # Needed for session

# Hardcoded username
USERNAME = "admin"
messages = []
# Load initial password or set default
if not os.path.exists("password.txt"):
    with open("password.txt", "w") as f:
        f.write("admin123")

def get_password():
    with open("password.txt", "r") as f:
        return f.read().strip()

@app.route('/')
def home():
    if 'user' in session:
        return render_template("index.html", username=session['user'])
    return redirect(url_for("login"))

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(get_password())  # Debugging line to check password
        if username == USERNAME and password == get_password():
            session['user'] = username
            return render_template("index.html")
        else:
            return "<h3>Login failed! Incorrect username or password.</h3>"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/change-password', methods=["GET", "POST"])
def change_password():
    if request.method == "POST":
        new_pass = request.form.get("password_new")
        confirm = request.form.get("password_conf")
        if new_pass == confirm:
            with open("password.txt", "w") as f:
                f.write(new_pass)
            return redirect(url_for("login"))
        return "<h3>Passwords do not match!</h3>"
    return render_template("change_password.html")

@app.route("/guestbook", methods=["GET", "POST"])
def guestbook():
    if request.method == "POST":
        name = request.form.get("name")
        msg = request.form.get("message")
        messages.append((name, msg))  # Unsafe: no sanitization!
        return redirect("/guestbook")
    return redirect("/guestbook")

if __name__ == '__main__':
    app.run(port=5000,debug=True)

