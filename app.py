from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import google.generativeai as genai
import os

# --------------------------------
# 🔧 Flask App Configuration
# --------------------------------
app = Flask(__name__, instance_relative_config=True)
app.secret_key = "mindsync_secret_key_very_secure"

# Ensure instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# 🗄️ MySQL Database Configuration (Make sure user_db exists)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:Rahul0316@localhost/user_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# --------------------------------
# 🤖 Gemini AI Setup
# --------------------------------
genai.configure(api_key="AIzaSyBG4WAl1-GiCZ5XozWbjPW1VJC0rQ7odA0")
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# --------------------------------
# 🧩 Database Models
# --------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat_history = db.relationship('ChatHistory', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()

# --------------------------------
# 🌐 Routes
# --------------------------------

# 🏠 Landing Page
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return redirect(url_for('home'))

# 👤 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        password = request.form.get('password')

        if not fullname or not email or not password:
            return render_template('register.html', error="All fields are required!")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return render_template('register.html', error="Email already registered!", fullname=fullname, email=email)

        new_user = User(fullname=fullname, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

# 🔑 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.fullname
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid email or password", email=email)

    return render_template('login.html')

# 🚪 Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# 🧭 Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session.get('user_name'))

# 💬 Chatbot (accessible for guests too)
@app.route('/chat')
def chatbot_page():
    return render_template('chatbot.html', user=session.get('user_name'))

# 🧠 Chatbot API (works for both guests & logged-in users)
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.json.get("message", "")

    try:
        response = chat.send_message(user_input)
        reply = response.text
    except Exception as e:
        print("Gemini Error:", e)
        reply = "⚠️ Sorry, I'm facing some issues connecting right now."

    # ✅ Only save if user logged in
    if 'user_id' in session:
        entry = ChatHistory(
            user_id=session['user_id'],
            user_message=user_input,
            bot_response=reply
        )
        db.session.add(entry)
        db.session.commit()

    return jsonify({"reply": reply})

# 🧍 Profile Page
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

# 🧾 Chat History
@app.route('/memory')
def memory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    history = ChatHistory.query.filter_by(user_id=session['user_id']).order_by(ChatHistory.timestamp.desc()).all()
    return render_template('memory.html', history=history, user=session.get('user_name'))

# 👥 Peer Community
@app.route('/peer')
def peer():
    return render_template('peercommunity.html')

# 👨‍⚕️ Doctor Page
@app.route('/doctor')
def doctor():
    return render_template('doctor.html')

# 🔁 Start New Chat
@app.route('/new')
def new_chat():
    global chat
    chat = model.start_chat()
    return redirect(url_for('chatbot_page'))

# --------------------------------
# 🚀 Run App
# --------------------------------
if __name__ == '__main__':
    app.run(debug=True)
