from first_flask_app import app
from flask import render_template, flash, request
from flask_login import login_required, current_user
from webforms import UserForm
from db_classes import Users
from db_config import db

# Create Dashboard Page
@app.route('/dashboard', methods =["GET","POST"])
@login_required
def dashboard():
   form = UserForm()
   id = current_user.id
   name_to_update = Users.query.get_or_404(id)
   if request.method == "POST":
      name_to_update.name = request.form['name']
      name_to_update.email = request.form['email']
      name_to_update.favorite_color = request.form['favorite_color']
      name_to_update.username = request.form['username']
      name_to_update.about_author = request.form['about_author']
      try:
         db.session.commit()
         flash("User Updated Successfully!")
         return render_template("dashboard.html", 
                                form=form,
                                name_to_update=name_to_update)
      except:
          flash("Error! Looks like there was a problem. Try again!")
          return render_template("dashboard.html", 
                                form=form,
                                name_to_update=name_to_update)
   else:
      return render_template("dashboard.html", 
                                form=form,
                                name_to_update=name_to_update,
                                id=id)   
   
