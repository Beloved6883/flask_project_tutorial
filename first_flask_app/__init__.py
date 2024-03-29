from flask import Flask

app = Flask(__name__)

# Avoiding a circular import
from first_flask_app import blog_views, dashboard_views, general_views, login_views, user_views
