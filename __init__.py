import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)


'''when we use form, we need to set secret key to protect modifying cookies, prevent csrf
    import secrets
    secrets.token_hex(16) 16-num of bytes
'''
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'    # where database is located. /// relative path from the current file
db = SQLAlchemy(app)         # SQLAlchemy database instance is created
bcrypt = Bcrypt(app)         # for hashing password


'''
    By default, when a user attempts to access a login_required view without being logged in, 
    Flask-Login will flash a message and redirect them to the log in view. 
    (If the login view is not set, it will abort with a 401 error.)
    
    The default message flashed is Please log in to access this page. 
    To customize the message, set LoginManager.login_message:
        login_manager.login_message = u"Bonvolu ensaluti por uzi tiun paĝon."
    To customize the message category, set LoginManager.login_message_category:
        login_manager.login_message_category = "info"
'''
login_manager = LoginManager(app)    # extension for login system so that users can login and logout
login_manager.login_view = 'login'   # set login route, the view that we pass is the function name for login
login_manager.login_message_category = 'info'   #info alert


''' For emails '''
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  #gmail
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('usert3244@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('Asdf123#')
# administrator list
#ADMINS = ['manishas053@gmail.com']
mail = Mail(app)   #initialize the instance

from ideaboard import routes     #Routes also imports app variable, cant import at top, will throw error
