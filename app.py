from flask import Flask, request, render_template, redirect, make_response
import os, secrets, bleach

app = Flask(__name__)

PASSWORD_FILE = 'password.txt'
COMMENTS_FILE = 'comments.txt'

users = {}
soldes = {}
username = "khawla"

# Load credentials from password.txt
def load_users():
    if not os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'w') as f:
            f.write('admin:admin123\nuser:user123\n')
    users = {}
    with open(PASSWORD_FILE, 'r') as f:
        for line in f:
            if ':' in line:
                username, password, sold= line.strip().split(':', 2)
                # print("line load users :")
                # print(line.strip().split(':', 2))
                users[username] = password
                soldes[username] = sold
    print("load users: ")
    print(users)
    print(soldes)
    return users


# Save credentials to password.txt
def save_users(users):
    print("save users: ")
    print(users)
    with open(PASSWORD_FILE, 'w') as f:
        for username, password in users.items():
            f.write(f"{username}:{password}:{soldes[username]}\n")


@app.route('/')
def index():
    username = request.cookies.get('username')
    usersold = request.cookies.get('usersold')
    users = load_users()
    if username in users:
        return render_template('index.html', username=username,usersold=usersold)
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    users = load_users()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
       
        if username in users and users[username] == password:
            resp = make_response(redirect('/'))
            resp.set_cookie('username', username,
                httponly=True,
                secure=True,
                samesite="Strict")
            resp.set_cookie('password', password,
                httponly=True,
                secure=True,
                samesite="Strict")
            resp.set_cookie('usersold', soldes[username],
                httponly=True,
                secure=True,
                samesite="Strict")
            return resp
        else:
            return "Invalid credentials", 403
    return render_template('login.html')


@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    # username = request.cookies.get('username')
    # users = load_users()
    # if not username or username not in users:
    #     return redirect('/login')
    
    users = load_users()
    if request.method == 'POST':
        new_pass = request.form.get('password_new')
        confirm_pass = request.form.get('password_conf')
        if new_pass == confirm_pass:
            users[username] = new_pass
            save_users(users)
            resp = make_response("Password changed successfully.")
            resp.set_cookie('password', new_pass)
            
            return redirect('/logout')
        else:
            return "Passwords don't match!"
    
    return render_template('change_password.html')

# @app.route("/change-password", methods=["GET", "POST"])
# def change_password():
#     # username = request.cookies.get('username')
#     # if not username:
#     #     return redirect("/login")
#     print("hello my friend !!")
#     if request.method == "GET":
#         token = secrets.token_hex(16)
#         resp = make_response(render_template("change_password.html", token=token))
#         resp.set_cookie("csrf_token", token)
#         return resp

#     if request.method == 'POST':
#         print("this is POST")
#         form_token = request.form.get("csrf_token")
#         cookie_token = request.cookies.get("csrf_token")
#         print(f"form token {form_token} cookie token {cookie_token}")
#         if (form_token is None and cookie_token is None) or form_token != cookie_token:
#             print("CSRF Token Mismatch! Request Blocked.")
#             return "CSRF Token Mismatch! Request Blocked.", 403
#         new_pass = request.form.get('password_new')
#         confirm_pass = request.form.get('password_conf')
#         if new_pass == confirm_pass:
#             users[username] = new_pass
#             save_users(users)
#             resp = make_response("Password changed successfully.")
#             resp.set_cookie('password', new_pass)
#             return redirect('/logout')
#         else:
#             return "Passwords don't match!"
    

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('username', '', expires=0)
    resp.set_cookie('password', '', expires=0)
    resp.set_cookie('usersold', '', expires=0)
    return resp

@app.route("/comments", methods=["GET", "POST"])
def comments():
    username = request.cookies.get('username')
    if not username:
        return redirect("/login")

    if request.method == "POST":
        comment = request.form.get("comment")
        safe_comment = bleach.clean(comment)
        with open(COMMENTS_FILE, "a") as f:
            f.write(f"{username}: {safe_comment}\n")
        return redirect("/comments")

    if not os.path.exists(COMMENTS_FILE):
        open(COMMENTS_FILE, "w").close()

    with open(COMMENTS_FILE, "r") as f:
        comments = f.readlines()

    return render_template("comments.html", comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
