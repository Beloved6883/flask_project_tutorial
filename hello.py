from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash


# Create a Flask instance
app = Flask(__name__)

# Add User Database (SQLite)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# New MySQL DB
db_password = os.getenv('MYSQL_PASSWORD')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{db_password}@localhost/users'

# Create CRSF token
app.config['SECRET_KEY'] = "my super secret key"

#Initialize the Database
app.app_context().push()
db = SQLAlchemy(app) 

# Migrate app with database
migrate = Migrate(app, db)

#Create a Model
class Users(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   name = db.Column(db.String(200), nullable=False)
   email = db.Column(db.String(120), nullable=False, unique=True)
   date_added = db.Column(db.DateTime, default=datetime.now)
   favorite_color = db.Column(db.String(120))

   # Do some password stuff
   password_hash = db.Column(db.String(128))

   @property
   def password(self):
      raise AttributeError('password is not a readable attribute')

   @password.setter
   def password(self,password):
      self.password_hash = generate_password_hash(password)
   
   def verify_password(self,password):
      return check_password_hash(self.password_hash, password)

   # Create a String
   def __repr__(self):
      return '<Name %r>' % self.name

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
   
# Create a Form Class
class NamerForm(FlaskForm):
   name = StringField("What's Your Name?", validators=[DataRequired()])
   submit = SubmitField('Submit')


class UserForm(FlaskForm):
   name = StringField("Name", validators=[DataRequired()])
   email = StringField("Email address", validators=[DataRequired()])
   favorite_color = StringField("Favorite Color")
   submit = SubmitField('Submit')

# Update Database record
@app.route('/update/<int:id>', methods=['GET','POST'])
def update(id):
   form = UserForm()
   name_to_update = Users.query.get_or_404(id)
   if request.method == "POST":
      name_to_update.name = request.form['name']
      name_to_update.email = request.form['email']
      name_to_update.favorite_color = request.form['favorite_color']
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
         user = Users(name=form.name.data, email = form.email.data, favorite_color = form.favorite_color.data)
         db.session.add(user)
         db.session.commit()
      name =form.name.data
      form.name.data = ""
      form.email.data = ""
      form.favorite_color.data = ""
      flash("User Added Sucessfully!")
   our_users = Users.query.order_by(Users.date_added)
   return render_template("add_user.html", form=form,
                          name=name, 
                          our_users=our_users)

@app.route('/')
def index():
    first_name = "Natasha"
    stuff = "this is bold text"
    favorite_pizza =["Pepperoni", "Cheese", "Meat Lovers", 41]

    return render_template("index.html", first_name = first_name, 
                           stuff=stuff, 
                           favorite_pizza=favorite_pizza)

# localhost:5000/user/Natasha
@app.route('/user/<name>')

def user(name):
    return render_template("user.html", user_name=name)

# Create custom error pages

# Invalid URL

@app.errorhandler(404)

def page_not_found(e):
 return render_template('404.html'), 404    

# Internal Server error
@app.errorhandler(500)

def internal_server_error(e):
 return render_template('500.html'), 500 

# Create Name Page (POST a form, GET a webpage)

@app.route('/name',methods=['GET','POST'])

def name():
   name = None
   form = NamerForm()

   #Validate Form
   if form.validate_on_submit():
      name = form.name.data
      form.name.data = ""
      flash("Form Submitted Successfully!")
   return render_template("name.html", 
                          name = name, 
                          form = form)
