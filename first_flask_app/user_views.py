from first_flask_app import app
from flask import render_template, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from webforms import UserForm
from db_config import db
from datetime import datetime
from flask_login import UserMixin
from db_classes import Users

# Create a route for deleting a record
@app.route('/delete/<int:id>')
def delete(id):
   user_to_delete = Users.query.get_or_404(id)
   name = None
   form = UserForm()

   try:
      db.session.delete(user_to_delete)
      db.session.commit()
      flash("User Deleted Successfully!!")
      our_users = Users.query.order_by(Users.date_added)
      return render_template("add_user.html", form=form,
                          name=name, 
                          our_users=our_users)
   except:
      flash("Whoops! There was problem deleting user. Try again.")
      return render_template("add_user.html", form=form,
                          name=name, 
                          our_users=our_users)
   

# Update Database record
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
   form = UserForm()
   name_to_update = Users.query.get_or_404(id)
   if request.method == "POST":
      name_to_update.name = request.form['name']
      name_to_update.email = request.form['email']
      name_to_update.favorite_color = request.form['favorite_color']
      name_to_update.username = request.form['username']
      try:
         db.session.commit()
         flash("User Updated Successfully!")
         return render_template("update.html", 
                                form=form,
                                name_to_update=name_to_update)
      except:
          flash("Error! Looks like there was a problem. Try again!")
          return render_template("update.html", 
                                form=form,
                                name_to_update=name_to_update)
   else:
      return render_template("update.html", 
                                form=form,
                                name_to_update=name_to_update,
                                id=id)   


#Jinja2 filters
#upper - all upper case letters
#lower - all lowercase letters
#capitalize - capitalizes the first letter of a word
#safe - passes html tags safely into the server (avoids hackers)
#striptags - removes html tages (keeps hackers from passing code through the website)
#title - capitalizes the first letter of each word in a string
#trim - removes trailing spaces

# Create a route decorator
@app.route('/user/add', methods=['GET','POST'])
def add_user():
   name = None
   form = UserForm()
   #Validate Form
   if form.validate_on_submit():
      user = Users.query.filter_by(email=form.email.data).first()
      if user is None:
         # Hash password
         hashed_pw = generate_password_hash(form.password_hash.data, "pbkdf2")
         user = Users(name=form.name.data, email = form.email.data, favorite_color = form.favorite_color.data,
                      password_hash = hashed_pw, username = form.username.data)
         db.session.add(user)
         db.session.commit()
      name =form.name.data
      form.name.data = ""
      form.email.data = ""
      form.favorite_color.data = ""
      form.password_hash.data = ""
      form.username.data = ""
      flash("User Added Sucessfully!")
   our_users = Users.query.order_by(Users.date_added)
   return render_template("add_user.html", form=form,
                          name=name, 
                          our_users=our_users)

