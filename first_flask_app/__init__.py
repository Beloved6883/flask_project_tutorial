from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_ckeditor import CKEditor

app = Flask(__name__)
ckeditor = CKEditor(app)

# Avoiding a circular import
from first_flask_app import blog_views, dashboard_views, general_views, login_views, user_views
