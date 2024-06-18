from first_flask_app import app
import os

print(os.path.exists(app.config['UPLOAD_FOLDER']))

print(app.config['UPLOAD_FOLDER'])
