from first_flask_app import app
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db_config import db


# Create a Blog Post mode
class Posts(db.Model):
   blog_id = db.Column(db.Integer, primary_key = True)
   title = db.Column(db.String(255))
   content = db.Column(db.Text)
   author = db.Column(db.String(255))
   date_posted = db.Column(db.DateTime, default=datetime.now)
   slug = db.Column(db.String(255)) 


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