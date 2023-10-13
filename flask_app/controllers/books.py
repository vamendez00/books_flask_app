from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models import user, book

# ******** ROOT ROUTE *********
@app.route("/users/dashboard/<int:id>")
def user_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data2={
        "id": session["logged_in_id"]
    }
    return render_template("dashboard.html", all_books=book.Book.get_all_books(), one_user=user.User.get_user_info(data2))

@app.route("/books/new_book")
def new_book():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    return render_template("create_book.html")

@app.route("/books/create_book", methods=["POST"])
def create_book():
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    
    if not book.Book.validate_book(request.form):
        return redirect("/books/new_book")

    book.Book.create_new_book(request.form)
    data={
        "id": session["logged_in_id"]
    }
    flash("Book added!", "book_add_success")
    return redirect(f"/users/dashboard/{session['logged_in_id']}")

# # ******** SHOW ONE book *********
@app.route("/books/show_book/<int:id>")
def book_page(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/")
    
    data={"id": id}
    data2={
        "id": session["logged_in_id"]
    }

    return render_template("show_book.html", book1=book.Book.get_one_book(data), users1= user.User.get_users_who_favored_book({"id": id}), user1=user.User.get_user_info(data2))


# ******** DELETE book *********
@app.route("/books/delete_book/<int:id>")
def delete(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={"id": id}
    book.Book.delete_book(id)
    return redirect(f"/users/dashboard/{session['logged_in_id']}")

# ******** DELETE book *********
@app.route("/books/delete_fav_book/<int:id>")
def delete_fav(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={"id": id}
    book.Book.delete_fav_book(id)
    return redirect(f"/users/account_info/{session['logged_in_id']}")


# *********** ADD TO FAVORITES ***********
@app.route("/books/favorites/<int:id>")
def fav_book(id):
    if "logged_in_id" not in session:
        flash("You must be logged in to view the requested page.", "login_required")        
        return redirect("/users")
    data={
        "book_id":id,
        "user_id":session['logged_in_id']
    }
    book.Book.add_fav_book(data)
    return redirect(f"/users/dashboard/{session['logged_in_id']}")