from flask import Flask, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from openai import OpenAI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Environment variables with better error handling
model = os.getenv("MODEL", "gpt-3.5-turbo")
api_key = os.getenv("API_KEY")
database_url = os.getenv("DATABASE_URL")
secret_key = os.getenv("SECRET_KEY")

# Validate critical environment variables
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")
if not database_url:
    raise ValueError("Database URL not found in environment variables")
if not secret_key:
    logger.warning("Secret key not found in environment variables, using random key")
    secret_key = os.urandom(24)

# Configure OpenAI client
client = OpenAI(api_key=api_key)

# Handle Render's Postgres URL format
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key
app.config['ENV'] = 'production'
app.config['DEBUG'] = False

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Create tables on startup
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")

# User credentials model
class UserCreds(db.Model):
    __tablename__ = 'new_user_creds'
    sNo = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=True)
    google_id = db.Column(db.String(200), unique=True)

    def __init__(self, name, email, password=None, google_id=None):
        self.name = name
        self.email = email
        self.password = password
        self.google_id = google_id

def create_db_table(email):
    table_name = f"{email.replace('@', '_').replace('.', '_')}_data"
    
    class Table(db.Model):
        __tablename__ = table_name
        sNo = db.Column(db.Integer, primary_key=True)
        prompt = db.Column(db.String(5000))
        responses = db.Column(db.String(8000))
        history = db.Column(db.JSON)
        timestamp = db.Column(db.DateTime, default=datetime.utcnow)
        
        __table_args__ = {'extend_existing': True}
        
        def __init__(self, prompt, responses, history, timestamp):
            self.prompt = prompt
            self.responses = responses
            self.history = history
            self.timestamp = timestamp
    
    with app.app_context():
        try:
            db.create_all()
            logger.info(f"Created table for {email}")
        except Exception as e:
            logger.error(f"Error creating table for {email}: {str(e)}")
    
    return Table

    @app.route("/", methods=['POST', 'GET'])
def signup_page():
    if request.method != 'POST':
        return render_template('signup.html')
    
    try:
        if request.is_json:
            data = request.json
            email = data.get("email")
            name = data.get("given_name")
            google_id = data.get("sub")
            if existing_email:
            if not all([email, name, google_id]):
                return jsonify({"success": False, "error": "Missing required fields"}), 400
            existing_email = UserCreds.query.filter_by(email=email).first()
            existing_email = UserCreds.query.filter_by(email=email).first()
            if existing_email:
                return jsonify({
                    "success": True,
                    "redirect_url": url_for('login_page')
                })
                return redirect(url_for('login_page'))
            new_user = UserCreds(name=name, email=email, google_id=google_id)
            db.session.add(new_user)
            db.session.commit()
            create_user_table(email)
            
            return jsonify({
                "success": True,
                "redirect_url": url_for('user_endpoint', username=name)
def login_page():
        else:
            name = request.form.get("name")
            email = request.form.get("email")
            password = request.form.get("password")
            password = data.get("ud")
            if not all([name, email, password]):
                flash("All fields are required!", "error")
                return redirect(url_for('signup_page'))
            if user and bcrypt.check_password_hash(user.password, password):
            existing_email = UserCreds.query.filter_by(email=email).first()
            if existing_email:
                flash("USER ALREADY EXISTS!", "error")
                return redirect(url_for('signup_page'))
                flash('Invalid Credentials, Please try again!', 'error')
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = UserCreds(name=name, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            create_user_table(email)
            
            flash('Registered Successfully!', 'success')
            return redirect(url_for('login_page'))
                username = user.name
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        flash('An error occurred during signup. Please try again.', 'error')
        return redirect(url_for('signup_page'))
@app.route("/login", methods=["POST", "GET"])
@app.route("/login", methods=["POST", "GET"])
def login_page():
    if request.method != 'POST':
        return render_template('login.html')
    user = UserCreds.query.filter_by(name=username).first()
    try:
        if request.is_json:
            data = request.json
            email = data.get("email")
            google_id = data.get("sub")
            user = UserCreds.query.filter_by(email=email, google_id=google_id).first()
            if user:
                return jsonify({
                    "success": True,
                    "redirect_url": url_for('user_endpoint', username=user.name)
                })
            return jsonify({"success": False, "error": "Invalid credentials"}), 401
        else:
            email = request.form.get("email")
            password = request.form.get("password")
        response = client.chat.completions.create(
            if not all([email, password]):
                flash('All fields are required!', 'error')
                return redirect(url_for('login_page'))
            temperature=0.4
            user = UserCreds.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                return redirect(url_for('user_endpoint', username=user.name))
        history.append({"role": 'assistant', "content": result})
            flash('Invalid Credentials, Please try again!', 'error')
            return redirect(url_for('login_page'))
@app.route("/<username>", methods=['POST', 'GET'])
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        flash('An error occurred during login. Please try again.', 'error')
        return redirect(url_for('login_page'))
        return redirect(url_for('user_endpoint', username=username, result=result, history=json.dumps(history)))
        
@app.route("/<username>", methods=['POST', 'GET'])
def user_endpoint(username):
    try:
        user = UserCreds.query.filter_by(name=username).first()
        if not user:
            return "User not found", 404
@app.route("/navigate_pages", methods=['POST'])
        table_model = create_db_table(user.email)
    selected_users = request.form.get("users")
        if request.method == 'POST':
            prompt_data = request.form.get("prompt_data")
            if not prompt_data:
                flash('Prompt data is required!', 'error')
                return redirect(url_for('user_endpoint', username=username))
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
            history = json.loads(request.form.get("history", "[]"))
            history.append({"role": "user", "content": prompt_data})
                    ],
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {'role': 'system', 'content': 'You are an assistant designed to extract key indicators and trading conditions from a given paragraph of information and generate a JSON file in a specific format structure.'},
                        *history
                    ],
                    max_tokens=600,
                    temperature=0.4
                )
                result = response.choices[0].message.content
                history.append({"role": 'assistant', "content": result})
                db.session.add(create_entry)
                create_entry = table_model(
                    prompt=prompt_data,
                    responses=result,
                    history=history,
                    timestamp=datetime.utcnow()
                )
                db.session.add(create_entry)
                db.session.commit()
                logger.error(f"Error in OpenAI API call: {str(e)}")
                return redirect(url_for('user_endpoint',
                                      username=username,
                                      result=result,
                                      history=json.dumps(history)))
        history = request.args.get('history', '[]')
            except Exception as e:
                logger.error(f"Error in OpenAI API call: {str(e)}")
                flash('Error processing your request. Please try again.', 'error')
                return redirect(url_for('user_endpoint', username=username))
                             username=username,
        result = request.args.get('result')
        history = request.args.get('history', '[]')
        chat_history = table_model.query.all()
        
        return render_template('interfaceTesting.html',
                             result=result,
                             username=username,
                             history=history,
                             chat_history=chat_history,
                             timestamp=datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S'))
    selected_users = request.form.get("users")
    except Exception as e:
        logger.error(f"Error in user endpoint: {str(e)}")
        return "An error occurred", 500

@app.route("/navigate_pages", methods=['POST'])
def navigate_pages():
    selected_users = request.form.get("users")
    if not selected_users:
        flash('No user selected!', 'error')
        return redirect(url_for('signup_page'))
    return redirect(url_for('user_endpoint', username=selected_users))

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
        return True
    except Exception as e:
def create_user_table(email):
    try:
        table_model = create_db_table(email)
        with app.app_context():
            db.create_all()
        return True
    except Exception as e:
        logger.error(f"Error creating user table: {str(e)}")
        return False

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            existing_users = UserCreds.query.all()
            for user in existing_users:
                create_user_table(user.email)
            logger.info("All user tables created successfully")
        except Exception as e:
            logger.error(f"Error in initialization: {str(e)}")
    
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)