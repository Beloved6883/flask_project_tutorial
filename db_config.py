from first_flask_app import app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

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
