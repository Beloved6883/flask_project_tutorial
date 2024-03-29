from first_flask_app import app
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash
from flask_login import login_user, login_required, logout_user, LoginManager
from webforms import LoginForm
from db_classes import Users

# Flask_Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
   return Users.query.get(int(user_id))

# Create Login Page
@app.route('/login', methods =["GET","POST"])
def login():
   form = LoginForm()
   if form.validate_on_submit():
      user = Users.query.filter_by(username=form.username.data).first()
      if user:
         # Check the password hash
         if check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Login Successful!")
            return redirect(url_for('dashboard'))
         else:
            flash("Wrong password. Try Again.")
      else:
         flash("That user does not exist! Try Again.")

   return render_template('login.html', form=form)

# Create logout function
@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
   logout_user()
   flash("You have been logged out. Thanks for stopping by!")
   return redirect(url_for('login'))

