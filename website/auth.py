from flask import Blueprint,render_template,request,flash,redirect,url_for
import re
from .models import User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from website.models import Schedule


# Make an expression that all Emails have.
regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
 
# Define a function for validating an Email
def check(email):
 
    # pass the regular expression and the string into the fullmatch() method to check the string passed in if it is a valid email
    if(re.fullmatch(regex, email)):
        print("Valid Email")
        return True
 
    else:
        print("Invalid Email")
        return False


# Tells flask to consider this file a blueprint (has routes to diffrent places)
auth = Blueprint('auth',__name__)

@auth.route("/login",methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password1')
        # Get user's info
        user = User.query.filter_by(email=email).first()
        #Check if user data matches login inputs 
        if user:
            if user.password == password:
                # If it does go to home page and log user in 
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')
    
    return render_template("login.html",  user=current_user)

@auth.route("/logout" ,methods=["GET","POST"])
@login_required
def logout():
    # Onclick redirect log user out and redirect to the login page.
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        ck = request.form.get("create_key")
        # Check if new acount can be made /  doesnt already exsist 
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif not check(email):
            flash("invalid email please re-enter", category="error")
        elif ck != "secret_key":
            flash('Invalid creation key please try again.', category='error')
        elif len(password1) < 8:
            flash('password must be 8 characters or more.', category='error') 
        elif password1 != password2:
            flash('passwords don\'t match.', category='error')
        elif len(first_name) < 2:
            flash('Name must be 2 characters or more.', category='error') 
        else:
            # Add the info of the acount to the system's database 
            new_user = User(email=email, first_name=first_name,password=password1)
            db.session.add(new_user)
            db.session.commit()
            flash("Sign up complete",category= "success")
            return redirect(url_for('views.home'))
        
        data= request.form
    return render_template("signup.html" ,  user=current_user)

