from flask import Flask, render_template, request, jsonify, redirect, url_for
import google.generativeai as genai
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__, instance_relative_config=True)
app.secret_key = "super-secret-key"

# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

# SQLite Database inside the instance folder
db_path = os.path.join(app.instance_path, "chat_history.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Gemini API Setup
API_KEY = "AIzaSyBG4WAl1-GiCZ5XozWbjPW1VJC0rQ7odA0"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat()

# -------------------- Database Model --------------------
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# -------------------- Routes --------------------

# Main Chat Page
@app.route("/")
def index():
    return render_template("chatbot.html")

# AI Chat API
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json["message"]
    response = chat.send_message(user_input)
    reply = response.text

    # Save to database
    entry = ChatHistory(user_message=user_input, bot_response=reply)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"reply": reply})

# Chat History Page
@app.route("/memory")
def memory():
    history = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()
    return render_template("memory.html", history=history)

# Start New Chat
@app.route("/new")
def new_chat():
    global chat
    chat = model.start_chat()
    return redirect(url_for("index"))

# Profile Placeholder
@app.route("/profile")
def profile():
    return render_template("profile.html")

# -------------------- Run App --------------------
if __name__ == "__main__":
    app.run(debug=True)
