from first_flask_app import app
from flask import render_template, flash, redirect, url_for
from werkzeug.security import check_password_hash
from webforms import PasswordForm, NamerForm, SearchForm
from db_classes import Users, Posts
from .blog_views import post
from flask_login import login_required, current_user

@app.route('/')
def index():
    first_name = "Natasha"
    stuff = "this is bold text"
    favorite_pizza =["Pepperoni", "Cheese", "Meat Lovers", 41]

    return render_template("index.html", first_name = first_name, 
                           stuff=stuff, 
                           favorite_pizza=favorite_pizza)

@app.route('/admin')
@login_required
def admin():
   id = current_user.id
   if id == 19:
      return render_template("admin.html")
   else:
      flash("You must be the admin to access this page.")
      return redirect(url_for('dashboard'))

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

# Pass stuff to the navbar
@app.context_processor
def base():
   form = SearchForm()
   return dict(form = form)

# Create search function
@app.route('/search', methods=["POST"])
def search():
   form = SearchForm()
   posts = Posts.query
   if form.validate_on_submit():
      # Get data from submitted form
      post.searched = form.searched.data

      # Query the database
      posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
      posts = posts.order_by(Posts.title).all()
      return render_template('search.html',
                             form=form,
                             searched = post.searched, posts=posts)