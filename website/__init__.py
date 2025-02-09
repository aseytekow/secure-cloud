from flask import Flask
from flask_login import LoginManager, UserMixin
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YOUR_SECRET_KEY'

flm = LoginManager()
flm.init_app(app)
flm.login_view = 'login'

conn = mysql.connector.connect(
    host = 'localhost',
    user = 'USERNAME',
    passwd = 'PASSWORD',
    database = 'SecureCloud'
)

cursor = conn.cursor()

class User(UserMixin):
    
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

@flm.user_loader
def load_user(id):
    cursor.execute(f"SELECT * FROM USERS WHERE ID = {id}")
    user = cursor.fetchone()
    if user:
        return User(user[0], user[1], user[2], user[3])
    return None

from website import routes
