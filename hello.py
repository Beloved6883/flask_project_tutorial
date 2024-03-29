from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user


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

# Flask_Login stuff
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
   return Users.query.get(int(user_id))

# Create Login Form
class LoginForm(FlaskForm):
   username = StringField("Username", validators=[DataRequired()])
   password = PasswordField("Password", validators=[DataRequired()])
   submit = SubmitField("Submit")

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
   

# Create a Blog Post mode
class Posts(db.Model):
   blog_id = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(255))
   content = db.Column(db.Text)
   author = db.Column(db.String(255))
   date_posted = db.Column(db.DateTime, default=datetime.now)
   slug = db.Column(db.String(255)) 

# Create a Posts Form
   
class PostForm(FlaskForm):
   title = StringField("Title", validators=[DataRequired()])
   content = StringField("Content", validators=[DataRequired()], widget=TextArea())
   author = StringField("Author", validators=[DataRequired()])
   slug = StringField("Slug", validators=[DataRequired()])
   submit = SubmitField("Submit")

# Add Post Page
@app.route('/add-post', methods=["GET","POST"])
# @login_required
def add_post():
   form = PostForm()

   if form.validate_on_submit():
      post = Posts(title = form.title.data,
                   content = form.content.data,
                   author = form.author.data,
                   slug = form.slug.data)
      # Clear the form
      form.title.data = ""
      form.content.data = ""
      form.author.data = ""
      form.slug.data = ""
   # Add post data to databased
      db.session.add(post)
      db.session.commit()
      
      #Return a message
      flash("Blog Post Submitted Successfully!")

      #Redirect to the webpage
   return render_template("add_post.html", form = form)

@app.route('/post/<int:id>')
def post(id):
   post = Posts.query.get_or_404(id)
   return render_template('post.html', post = post)

@app.route('/posts/edit/<int:id>', methods =["GET","POST"])
@login_required
def edit_post(id):
   post = Posts.query.get_or_404(id)
   form = PostForm()
   if form.validate_on_submit():
      post.title = form.title.data
      post.author = form.author.data
      post.slug = form.slug.data
      post.content = form.content.data

      # Update database
      db.session.add(post)
      db.session.commit()
      flash("Post Has Been Updated!")
      return redirect(url_for('post',id=post.blog_id))

# Pass in form information
   form.title.data = post.title
   form.author.data = post.author
   form.slug.data = post.slug
   form.content.data = post.content
   return render_template('edit_post.html', form=form)
# Add blog post listing page

# Delete blog post
@app.route('/posts/delete/<int:id>')
def delete_post(id):
   post_to_delete = Posts.query.get_or_404(id)

   try:
      db.session.delete(post_to_delete)
      db.session.commit()

      # Return a message
      flash("Blog Post Was Deleted!")

      posts = Posts.query.order_by(Posts.date_posted)
      return render_template ("posts.html",
                           posts = posts)

   except:
      flash("Whoops! There was a problem deleting post. Try again.")
      posts = Posts.query.order_by(Posts.date_posted)
      return render_template ("posts.html",
                           posts = posts)

@app.route('/posts')
def posts():
   # Grab all the posts from the database
   posts = Posts.query.order_by(Posts.date_posted)
   return render_template ("posts.html",
                           posts = posts)

# JSON thing

@app.route('/date')
def get_current_date():
   favorite_pizza ={"John":"Pepperoni",
                    "Mary": "Cheese",
                    "Tim": "Meat Lovers"}
   return favorite_pizza
   # return {"Date": date.today()}


#Create a Datebase Model
class Users(db.Model, UserMixin):
   id = db.Column(db.Integer, primary_key=True)
   username = db.Column(db.String(20), nullable = False, unique = True)
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

# Create a Form Class
class PasswordForm(FlaskForm):
   email = StringField("What's Your Email?", validators=[DataRequired()])
   password_hash = PasswordField("What's Your Password?", validators=[DataRequired()])
   submit = SubmitField('Submit')

class UserForm(FlaskForm):
   name = StringField("Name", validators=[DataRequired()])
   username = StringField("Username", validators=[DataRequired()])
   email = StringField("Email address", validators=[DataRequired()])
   favorite_color = StringField("Favorite Color")
   password_hash = PasswordField('Password',validators=[DataRequired(), EqualTo('password_hash2', message='Password Must Match!')])
   password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
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

# Create password test page
@app.route('/test_pw',methods=['GET','POST'])

def test_pw():
   email = None
   password = None
   pw_to_check = None
   passed = None

   form = PasswordForm()

   #Validate Form
   if form.validate_on_submit():
      email = form.email.data
      password = form.password_hash.data
      #Clear the form
      form.email.data = ""
      form.password_hash.data=""

      # Look up user by email

      pw_to_check = Users.query.filter_by(email=email).first()
      
      # Check hashed Password (true or false returned)
      passed = check_password_hash(pw_to_check.password_hash, password)

      #flash("Form Submitted Successfully!")
   return render_template("test_pw.html", 
                          email = email, 
                          password = password,
                          form = form,
                          pw_to_check = pw_to_check,
                          passed = passed)

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
