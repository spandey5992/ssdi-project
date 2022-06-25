from flask import Blueprint, render_template, redirect, url_for, request, flash
from . import db
from .models import User
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

userRoutes = Blueprint("userRoutes", __name__)

@userRoutes.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in!", category='success')
                login_user(user, remember=True)
                return redirect(url_for('blogRoutes.home'))
            else:
                flash('Password incorrect.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html")


@userRoutes.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        firstName = request.form.get("firstname")
        lastName = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")


        if User.query.filter_by(email=email).first():
            flash('Email already used.', category='error')
        elif User.query.filter_by(username=username).first():
            flash('Username already used', category='error')
        else:
            new_user_details = User(firstname=firstName, lastname=lastName, email=email, username=username, password=generate_password_hash(password, method='sha256'))
            
            db.session.add(new_user_details)
            db.session.commit()
            
            login_user(new_user_details, remember=True)
            flash('User created!')
            
            return redirect(url_for('blogRoutes.home'))

    return render_template("signup.html")


@userRoutes.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Successfully Logged Out!', category='success')
    return redirect(url_for("userRoutes.login"))


@userRoutes.route("/edituser", methods=['GET', 'POST'])
@login_required
def edituser():
    if request.method == 'POST':
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        db.session.query(User).filter(User.id==current_user.id).update({'firstname':firstname, 
                                                        'lastname':lastname, 
                                                        'username':username,
                                                        'email':email,
                                                        'password':generate_password_hash(password, method='sha256')})
        db.session.commit()
        flash('Details updated successfully', category='success')
        return redirect(url_for('blogRoutes.home'))
    return render_template("userEdit.html")
