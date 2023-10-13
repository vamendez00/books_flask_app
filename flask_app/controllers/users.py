from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models import user

# ******** ROOT ROUTE *********
@app.route("/")
def index():
    return redirect("/users")

@app.route("/users")
def user_forms():
    users=user.User.get_all()
    return render_template("login_and_reg.html", all_users=users)


# ******** ADD/CREATE NEW user *********
@app.route("/users/create_user", methods=["POST"])
def create_user():
    
    if not user.User.validate_user_registration(request.form):
        return redirect("/")
    
    hashed_pw=bcrypt.generate_password_hash(request.form["password"])

    data={
        "f_name":request.form["f_name"],
        "l_name":request.form["l_name"],
        "email":request.form["email"],
        "password":hashed_pw,
    }

    one_user_id=user.User.create_new_user(data)
    session["logged_in_id"]=one_user_id
    flash("Registration successful. You are now logged in!", "user_registration_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")   

# ******** user login *********
@app.route("/users/user_login", methods=["POST"])
def user_login():
    one_user= user.User.validate_login(request.form)

    if not one_user:
        return redirect("/")
    
    session["logged_in_id"]=one_user.id
    flash("Login successful!", "user_login_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")



# ******** ACCOUNT INFO & UPDATE *********

@app.route("/users/account_info/<int:id>")
def account_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")
        return redirect("/")
    
    data={"id":id}
    user1=user.User.get_user_with_books(data)
    data2={"id": session["logged_in_id"]
    }

    return render_template("account_info.html", one_user=user1, favBooks=user.User.get_user_with_favorite_books(data), current_user=user.User.get_user_info(data2))

@app.route("/users/update_user", methods=["POST"])
def update_user():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")
        return redirect("/users")
        
    if not user.User.validate_user_update(request.form):
        return redirect(f"/users/account_info/{session['logged_in_id']}")
    user.User.update_user(request.form)
    flash("User update SUCCESSFUL!", "user_update_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")

# ******** LOGOUT *********
@app.route("/users/user_logout")
def logout():
    session.clear()
    return redirect("/")