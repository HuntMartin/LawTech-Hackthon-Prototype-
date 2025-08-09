from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from transformers import DistilBertForQuestionAnswering, DistilBertTokenizer, Trainer
import torch
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS
from datasets import load_dataset, Dataset

app = Flask(__name__)

CORS(app)
# Load pretrained model and tokenizer
model_name = "distilbert-base-uncased-distilled-squad"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForQuestionAnswering.from_pretrained(model_name)
model.eval()  # evaluation mode

app.secret_key = 'testing123'  # change this to a secure random key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identity = db.Column(db.String(150), unique=False, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(30), unique=False, nullable=False)
    Age = db.Column(db.Integer, unique=False, nullable=False)
    Monthly_Income = db.Column(db.Integer, unique=False, nullable=False)
    LivingCondition = db.Column(db.String(40), unique=False, nullable=False)
    Problem = db.Column(db.String(150), unique=False, nullable=False)
# Load your reference context text ONCE at startup

with open('context.txt', 'r', encoding='utf-8') as f:
    CONTEXT = f.read()



#Load Json File as context for letting AI model to learn, needs train data in one python script and opt then deploy here with AI model otherwise size cant be allowed
"""
with open('nz-ssa-245-en.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Assume JSON is a list of text passages:
passages = []
passages = [entry['c'] for entry in data]

# Combine all passages into one big context string
CONTEXT = "\n\n".join(passages)
"""
#Building APIs below
@app.route('/')
def home():
    print(session.get('user_identity'))
    if session.get('user_identity') == "applicant":
        return redirect(url_for('applicant'))
    elif session.get('user_identity') == "staff":
        return redirect(url_for('staffReview'))
    else:
        return redirect(url_for('login'))

@app.route('/staffReview')
def staffReview():
    if session.get('user_identity') != 'staff':
        return redirect(url_for('login'))
    return render_template('staffReview.html')

@app.route('/applicant')
def applicant():
    if session.get('user_identity') != 'applicant':
        return redirect(url_for('login'))
    return render_template('applicant.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['user_identity'] = user.identity

            flash("Logged in successfully!")
            if user.identity == 'staff':
                return redirect(url_for('staffReview'))
            if user.identity == 'applicant':
                return redirect(url_for('applicant'))
        else:
            flash("Invalid username or password.")
            return jsonify({"success": False, "message": "Invalid username or password"}), 401

    return render_template('login.html')

#The AI api below is AI model one which needs to be trained with the collected data and could be a heavy work with a few months

@app.route('/AImodel', methods=['POST'])
def AImodel():
    # Read question from file instead of from request JSON
    try:
        with open('question.txt', 'r', encoding='utf-8') as f:
            question = f.read().strip()
    except Exception as e:
        return jsonify({"error": f"Failed to read question file: {str(e)}"}), 500

    if not question:
        return jsonify({"error": "Question file is empty"}), 400

    context = CONTEXT  # loaded at app startup

    inputs = tokenizer.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        start_scores = outputs.start_logits
        end_scores = outputs.end_logits

    start_idx = torch.argmax(start_scores)
    end_idx = torch.argmax(end_scores) + 1

    answer_tokens = input_ids[0][start_idx:end_idx]
    answer = tokenizer.decode(answer_tokens, skip_special_tokens=True).strip()

    if not answer:
        answer = "Sorry, I could not find an answer."

    return jsonify({"answer": answer})


### Private Tinfoil invoke
import requests

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = requests.post('http://localhost:5000/ask', json={"question": question})
    if response.status_code == 200:
        return jsonify({"answer": response.json().get('answer')})
    else:
        return jsonify({"error": "AI service failed"}), 500

# SQLAlchemy model
@app.route("/applicants", methods=["GET"])
def get_applicants():
    applicants = Applicant.query.all()
    data = []
    for applicant in applicants:
        data.append({
            "id": applicant.id,
            "Name": applicant.Name,
            "Age": applicant.Age,
            "Monthly_Income": applicant.Monthly_Income,
            "LivingCondition": applicant.LivingCondition,
            "Problem": applicant.Problem
        })
    return jsonify(data)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
