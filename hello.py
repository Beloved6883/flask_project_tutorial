from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# Create a Flask instance

app = Flask(__name__)

# Create CRSF token
app.config['SECRET_KEY'] = "my super secret key"

# Create a Form Class
class NamerForm(FlaskForm):
   name = StringField("What's Your Name?", validators=[DataRequired()])
   submit = SubmitField('Submit')


# Create a route decorator

#Jinja2 filters
#upper - all upper case letters
#lower - all lowercase letters
#capitalize - capitalizes the first letter of a word
#safe - passes html tags safely into the server (avoids hackers)
#striptags - removes html tages (keeps hackers from passing code through the website)
#title - capitalizes the first letter of each word in a string
#trim - removes trailing spaces


@app.route('/')

# def index():
#     return "<h1>Hello World!</h1>"

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
