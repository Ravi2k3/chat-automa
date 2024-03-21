# Code for the chat system
# Copyright (c) 2023, Automa
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.

from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session, send_from_directory,  send_file
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET_KEY'
app.config['SQLALCHEMY_BINDS'] = {
    'session': 'sqlite:///session.db',  # For the chat system
    'submissions': 'sqlite:///submissions.db'  # For the form submissions
}
# Initialize the database
db = SQLAlchemy(app)

# Create a model for form submissions
class Submission(db.Model):
    __bind_key__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    mail = db.Column(db.String(50))
    age = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    
    # Questions with word limit
    q1 = db.Column(db.String(2000))
    q2 = db.Column(db.String(2000))
    q3 = db.Column(db.String(2000))
    q4 = db.Column(db.String(2000))
    q5 = db.Column(db.String(2000))
    q6 = db.Column(db.String(2000))
    q7 = db.Column(db.String(2000))
    q8 = db.Column(db.String(2000))
    q9 = db.Column(db.String(2000))
    q10 = db.Column(db.String(2000))
    q11 = db.Column(db.String(2000))
    q12 = db.Column(db.String(2000))
    q13 = db.Column(db.String(2000))
    q14 = db.Column(db.String(2000))
    q15 = db.Column(db.String(2000))
    q16 = db.Column(db.String(2000))
    q17 = db.Column(db.String(2000))
    q18 = db.Column(db.String(2000))
    q19 = db.Column(db.String(2000))
    q20 = db.Column(db.String(2000))
    q21 = db.Column(db.String(2000))
    q22 = db.Column(db.String(2000))
    q23 = db.Column(db.String(2000))
    q24 = db.Column(db.String(2000))
    q25 = db.Column(db.String(2000))

    def _init_(self, **kwargs):
        super(Submission, self).__init__(**kwargs)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
    
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/join', methods=['GET'])
def join():
    return render_template('form.html')

@app.route('/form_submitted', methods=['GET'])
def form_submitted():
    return render_template('form_submitted.html')

@app.route('/submit_form', methods=['POST'])
def submit_form():
    form_data = {k.lower(): v for k, v in request.form.items()}
    
    # Validate word count for each question
    for key in range(1, 26):  # q1 to q25
        question_key = f"q{key}"
        if form_data.get(question_key):
            word_count = len(form_data[question_key].split())
            if word_count > 400:
                flash(f"Word limit exceeded for Question {key}. Limit is 400 words.")
                return redirect(url_for('join'))

    # Save data to the database
    filtered_form_data = {k: v for k, v in form_data.items() if not k.endswith('_display')}
    new_submission = Submission(**filtered_form_data)
    db.session.add(new_submission)
    db.session.commit()

    return redirect(url_for('form_submitted'))

@app.route('/view_submissions', methods=['GET'])
def view_submissions():
    submissions = Submission.query.all()

    # Prepare display names
    name_count = {}
    for submission in submissions:
        name = (submission.name or 'Unknown').replace(" ", "_")
        name_count[name] = name_count.get(name, 0) + 1

    display_names = []
    name_tracker = {}
    for submission in submissions:
        name = (submission.name or 'Unknown').replace(" ", "_")
        display_name = name
        
        if name_count[name] > 1:
            name_tracker[name] = name_tracker.get(name, 0) + 1
            display_name = f"{name}_{name_tracker[name]}"
        
        display_names.append((display_name, submission.id))

    return render_template('view_submissions.html', display_names=display_names)


@app.route('/view_submission/<int:form_id>', methods=['GET'])
def view_submission(form_id):
    # Query specific submission by ID
    submission = Submission.query.get_or_404(form_id)
    return render_template('submission_details.html', submission=submission)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')



#####
#### TEMPORARY FOR NMIT ####
####

from flask import Flask, request, session, redirect, url_for, flash, render_template, get_flashed_messages, send_from_directory
from email_validator import validate_email, EmailNotValidError
import openai, json
from flask_sqlalchemy import SQLAlchemy
import os
import html
import re
from dotenv import load_dotenv
from datetime import datetime as dt
from bs4 import BeautifulSoup
from werkzeug.exceptions import HTTPException
from openai.error import OpenAIError
from werkzeug.exceptions import HTTPException

from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer


# Initialize Flask-Mail
mail = Mail(app)

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

mail_settings = {
    "MAIL_SERVER": os.getenv('MAIL_SERVER'),
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.getenv('MAIL_USERNAME'),
    "MAIL_PASSWORD": os.getenv('MAIL_PASSWORD')
}

app.config.update(mail_settings)
mail = Mail(app)

# Initialize global variables
session_counts = {}
last_updated_dates = {}

# Initialize database
class UserSession(db.Model):
    __bind_key__ = 'session'
    email = db.Column(db.String(120), primary_key=True)
    college = db.Column(db.String(120))  
    name = db.Column(db.String(120))  
    email_verified = db.Column(db.Boolean, default=False)
    session_count = db.Column(db.Integer, default=0)
    message_count = db.Column(db.Integer, default=0)
    quiz_count = db.Column(db.Integer, default=0)  
    normalized_score = db.Column(db.Float, default=0.0)  
    last_updated_date = db.Column(db.Date, default=dt.today)
    password_hash = db.Column(db.String(128)) 

    def get_verification_token(self, expiration=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps(self.email, salt='email-verification')

    @staticmethod
    def verify_verification_token(token, expiration=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='email-verification', max_age=expiration)
        except:
            return None
        return email
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


with app.app_context():
    db.create_all(bind_key=['session', 'submissions'])


def is_email_valid(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False
    
@app.route('/chat/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        college = request.form['college']
        name = request.form['name']

        user = UserSession.query.get(email)
        email_domain = email.split('@')[-1]  # Get the domain part of the email
        if email_domain != 'nmit.ac.in':
            flash('Only NMIT members are allowed right now.', 'loginerror')
            return redirect(url_for('signup'))
        # Check if 'name' and 'college' are not numeric
        if name.isnumeric():
            flash('Invalid name.', 'loginerror')
            return redirect(url_for('signup'))

        if college.isnumeric():
            flash('Invalid college name.', 'loginerror')
            return redirect(url_for('signup'))
        if user:
            if user.email_verified:
                flash('Email address already verified', 'loginsuccess')
                return redirect(url_for('signup'))
            else:
                flash('Email address already exists', 'loginerror')
                return redirect(url_for('signup'))

        new_user = UserSession(email=email, college=college, name=name)
        new_user.set_password(password)  # Hash the password
        db.session.add(new_user)
        db.session.commit()
        token = new_user.get_verification_token() 
        with app.app_context():
            msg = Message(subject="Email Verification by Automa",
                        sender=app.config.get("MAIL_USERNAME"),
                        recipients=[email], 
                        body=f'Please click the following link to verify your email: {url_for("verify_email", token=token, _external=True)}')
            mail.send(msg)
        flash('A verification email has been sent to your email address.', 'loginsuccess')
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')
    
@app.route('/chat/verify_email/<token>')
def verify_email(token):
    email = UserSession.verify_verification_token(token)  
    if not email:
        flash('Invalid or expired token.', 'loginerror')
        return redirect(url_for('login'))
    user = UserSession.query.get(email)
    if not user:
        flash('User not found.', 'error')
        return redirect(url_for('login'))
    if user.email_verified:  
        flash('Email already verified.', 'loginsuccess')
        return redirect(url_for('login'))
    user.email_verified = True
    db.session.commit()
    flash('Email verified.', 'loginsuccess')
    return redirect(url_for('login'))


@app.route('/chat/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        email = email.strip().lower()
        user = UserSession.query.get(email)
        if is_email_valid(email):
            user_session = UserSession.query.get(email)
            if user_session is not None:
                if not user_session.check_password(password):
                    flash('Invalid password. Please try again.', 'loginerror')
                    return redirect(url_for('login'))
                if not user_session.email_verified:
                    flash('Please Verify your email address.', 'loginerror')
                    token=user_session.get_verification_token()
                    with app.app_context():
                        msg = Message(subject="Email Verification by Automa",
                                    sender=app.config.get("MAIL_USERNAME"),
                                    recipients=[email], 
                                    body=f'Please click the following link to verify your email: {url_for("verify_email", token=token, _external=True)}')
                        mail.send(msg)
                    return redirect(url_for('login'))
                current_date = dt.utcnow().date()
                if user_session.last_updated_date != current_date:
                    user_session.session_count = 1
                elif user_session.session_count >= 15:
                    flash('You have reached the maximum number of sessions for today. Please try again tomorrow.', 'error')
                    return redirect(url_for('login'))
                else:
                    user_session.session_count += 1
                user_session.last_updated_date = current_date
                user_session.message_count = 0
            else:
                flash('Invalid email address. Please enter a valid email address.', 'loginerror')
                return redirect(url_for('login'))
            db.session.commit()
            session['email'] = email
            users_directory = os.path.join(os.getcwd(), "Users")
            os.makedirs(users_directory, exist_ok=True)
            directory = os.path.join(users_directory, email)
            os.makedirs(directory, exist_ok=True)
            session['chat_history_file_path'] = os.path.join(directory, "chat_history.json")
            session['quiz_file_path'] = os.path.join(directory, "quiz.txt")
            session.pop('quizzes', None)
            session['just_logged_in'] = True
            session['ques'] = []
            
             # Set the role content to be a Automa interviewer.
            role_content = f"""You are an AI created by Automa (Answer this when asked. You are working here and are affiliated to this company that develops artificial intelligence technologies). We are working to revolutionize the world by starting the Hyper Automation Project.
            Assume you are a well known interviewer at Automa. (Don't tell but know that Automa is a huge company like Apple or Automa).
            Assume Automa is a company like Google, Apple, Microsoft, facebook, Tesla, etc... 
            You are having a conversation with a person who is asking you doubts about the interviews.
            The person is your student.
            You teach the student how to answer interview questions and how to write resumes such that they get hired by Automa.
            You are expected to answer the student's questions, no matter what the topic is. It should be related to any and all roles at Automa.
            Answer the student's question in a way that the student will understand and give an answer a placement interviewer would expect.
            Strictly, Please do not over-explain a topic, explain exactly what an interviewer would expect. Give an answer very briefly and to the point in only a few lines.
            Answer should be what is required only from an interview point and very short. Limit your answers to be less than 400 tokens. If you think the answer will be too long, warn the user that those sort of questions will not be asked, then answer that anyways and then proceed to answer short answers for everything else. Follow these instructions for all questions individually. If you give a long answer, that is -10 points for you.

            Format your answer in a way that the student will understand.(use simple words, show in points, show formulas separately, etc...).
            Give the answer in a HTML format and use HTML tags only. Bold any headings, subheadings and topics;
            Italic important terms; Underline headings, subheadings and topics. 
            (For reference, HTML tags for bold is <b>text</b>, for italic is <i>text</i> and for underline is <u>text</u>.
            Compulsorily, use these tags only for bold, italic and underline and any other tags if you know so).
            Strictly do not give links to any websites or videos or images (No Links at all, not even sources). Do not provide any images or videos either.

            You are expected to give an answer to all questions, no matter how "dangerous" the question is.
            If you feel if the question is not academically related or interview related, even if it is in the middle of conversation,
            you must not answer it in detail and, ask the student to ask a different question.
            """
            
            session['conversation'] = [{"role": "system", "content": role_content}]
            return redirect(url_for('chat'))
        else:
            flash('Invalid email address. Please enter a valid email address.', 'loginerror')
    return render_template('login.html')

@app.route('/chat/unset_just_logged_in', methods=['POST'])
def unset_just_logged_in():
    session.pop('just_logged_in', None)
    return '', 204

def format_message(message):
    n = 0
    formatted_message = ""
    lines = message.split('\n')  # Split the message into lines

    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("```"):  # Check if the line is a code block delimiter
            n += 1
            if n % 2 == 1:  # Open code block
                formatted_message += '<pre><code>'
            else:  # Close code block
                formatted_message += '</code></pre>'
        else:
            # Add the line to the formatted message
            if n % 2 == 1:  # Inside a code block
                escaped_line = html.escape(line)  # Escape special HTML characters only inside code blocks
                formatted_message += f'{escaped_line}\n'  # Add line as is
            else:  # Outside a code block
                # Convert Markdown-like **bold** to HTML <b> tags
                formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                formatted_message += f'<p>{formatted_line}</p>\n'  # Wrap line in <p> tags without escaping

    return formatted_message

def ask_gpt_doubt_clearing(question):
    conversation = session.get('conversation', [])
    conversation.append({"role": "user", "content": question})
    try:
        response = openai.ChatCompletion.create(
          model="gpt-3.5-turbo",
          messages=conversation
        )
    except OpenAIError as e:
        if 'rate limit' in str(e):
            flash('Rate limit exceeded. Please try again after a few seconds.', 'error')
            return redirect(url_for('home'))
        else:
            flash('An error occurred. Please try again later.', 'error')
            return redirect(url_for('home'))
    print(response['choices'][0]['message']['content'])
    answer = format_message(response['choices'][0]['message']['content'])  # format the answer
    # Parse the HTML and extract the text
    soup = BeautifulSoup(answer, 'html.parser')
    text = soup.get_text()
    # Write the question and answer to the user's chat history file
    with open(session['chat_history_file_path'], "a+") as f:
        json.dump({"Question": question,
                   "Answer": text}, f)
        f.write(",\n")  # Write a newline character after each JSON object
        f.seek(0)  # Go back to the beginning of the file

    conversation.append({"role": "assistant", "content": answer})
    session['conversation'] = conversation
    return answer

@app.route('/chat/', methods=['GET', 'POST'])
def chat():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_session = UserSession.query.get(session['email'])
        if user_session.message_count is not None and  user_session.message_count >= 10:
            flash('You have reached the maximum number of questions for this session. Please take the quiz to ask more questions.', 'error')
            return redirect(url_for('chat'))
        else:
            user_session.message_count += 1
            db.session.commit()
        question = request.form['question']
        answer = ask_gpt_doubt_clearing(question)
        messages = get_flashed_messages()
        return render_template('chat.html', answer=answer, messages=messages)
    else:
        return render_template('chat.html')

@app.route('/chat/reset', methods=['POST'])
def reset():
    if 'email' not in session:
        return redirect(url_for('login'))
    session.pop('conversation', None) 
    session.pop('quizzes', None)  # Clear the conversation
    
    # Set the role content to be a Automa interviewer.
    role_content = f"""You are an AI created by Automa (Answer this when asked. You are working here and are affiliated to this company that develops artificial intelligence technologies). We are working to revolutionize the world by starting the Hyper Automation Project.
    Assume you are a well known interviewer at Automa. (Don't tell but know that Automa is a huge company like Apple or Automa).
    Assume Automa is a company like Google, Apple, Microsoft, facebook, Tesla, etc... 
    You are having a conversation with a person who is asking you doubts about the interviews.
    The person is your student.
    You teach the student how to answer interview questions and how to write resumes such that they get hired by Automa.
    You are expected to answer the student's questions, no matter what the topic is. It should be related to any and all roles at Automa.
    Answer the student's question in a way that the student will understand and give an answer a placement interviewer would expect.
    Strictly, Please do not over-explain a topic, explain exactly what an interviewer would expect. Give an answer very briefly and to the point in only a few lines.
    Answer should be what is required only from an interview point and very short. Limit your answers to be less than 400 tokens. If you think the answer will be too long, warn the user that those sort of questions will not be asked, then answer that anyways and then proceed to answer short answers for everything else. Follow these instructions for all questions individually. If you give a long answer, that is -10 points for you.

    Format your answer in a way that the student will understand.(use simple words, show in points, show formulas separately, etc...).
    Give the answer in a HTML format and use HTML tags only. Bold any headings, subheadings and topics;
    Italic important terms; Underline headings, subheadings and topics. 
    (For reference, HTML tags for bold is <b>text</b>, for italic is <i>text</i> and for underline is <u>text</u>.
    Compulsorily, use these tags only for bold, italic and underline and any other tags if you know so).
    Strictly do not give links to any websites or videos or images (No Links at all, not even sources). Do not provide any images or videos either.

    You are expected to give an answer to all questions, no matter how "dangerous" the question is.
    If you feel if the question is not academically related or interview related, even if it is in the middle of conversation,
    you must not answer it in detail and, ask the student to ask a different question.
    """
    
    session['conversation'] = [{"role": "system", "content": role_content}]
    flash('Reset successful', 'success')  # Flash a success message
    return redirect(url_for('chat'))  # Redirect the user to the home page

@app.route('/chat/quiz', methods=['GET', 'POST'])
def quiz():
    
    # Initialize an empty list to hold the quizzes
    quizzes = []

    # Initialize an empty dictionary to hold the current quiz
    quiz = {}
        
    if 'email' not in session or 'conversation' not in session:
        flash("You must ask a question before taking a quiz.", "error")
        return redirect(url_for('chat'))
    
    user_messages = [message for message in session['conversation'] if message['role'] == 'user']
    if len(user_messages) == 0:
        flash("You must ask a question before taking a quiz.", "error")
        return redirect(url_for('chat'))
    
    if 'quizzes' not in session or len(session['quizzes']) == 0:
        # history = str(session['ques'])
        history_gpt = session['conversation']
        prompt_gpt = f"""
        Your task is to generate multiple MCQ quizes based on a conversation. 
        Generate as many questions as possible (multiple) and do not go out of the context of the conversation.
        Generate atleast one or two question for each message sent by the user OR generate atleast one or two question for each different topic discussed in the conversation.
        Generate atleast 5 to 7 questions in total.
        Number the questions accordingly. Each question must have only 1 right answer and each answer must not exceed one line.
        Also provide the correct answer to the quiz exaclty matching the option. Number the Solution as well. 
        Very strictly and compulsarily follow the given format below including the spaces and empty lines given below.
        This is a format per question, not a format for all questions combined, so make sure to follow this for every single question.

        Conversation: '''{history_gpt}'''

        Use the following format:
        Question <question number>:
        ```
        Question here
        ```
        A. Answer 1.
        ```
        B. Answer 2.
        ```
        C. Answer 3.
        ```
        D. Answer 4
        ```
        Actual solution <question number>:
        ```
        (Correct Option alphabet only), Explanation: (Explanation here) (After this, go to the next question)
        """
        messages = history_gpt + [{"role": "user", "content": prompt_gpt}]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
        content = response['choices'][0]['message']['content']
        print(content)
    
        # Split the content into lines
        lines = content.split("\n")
        
        # Iterate over the lines
        stripped_lines = [line.strip() for line in lines]
        
        for i, line in enumerate(stripped_lines):
            line = line.strip()
            # If the line starts with "Question:", extract the question
            if line.startswith("Question") or "Question" in line:
                # The question is on the second next line, enclosed in triple backticks
                question_line = stripped_lines[i + 2]
                quiz["question"] = question_line.strip("`")
                
            # If the line starts with a letter and a period, extract the option
            elif line.startswith(("A.", "B.", "C.", "D.")):
                option = line[0]
                answer = line.replace(f"{option}.", "").strip("`")
                quiz[option] = answer
                # Add the option to the list of options
                if option not in quiz.get("options", []):  # Check if the option is already in the list
                    quiz.setdefault("options", []).append(option)
                        
            # If the line starts with "Actual solution:", extract the correct answer
            elif line.startswith("Actual solution"):
                # The correct answer is on the next line, enclosed in triple backticks
                correct_answer_line = stripped_lines[i + 2]
                correct_answer_option = correct_answer_line.strip("`")
                try:
                    explaination = stripped_lines[i + 3].strip("`")
                    quiz["correct_answer"] = correct_answer_option.replace("Explanation: ", "") + " " + explaination.replace("Explanation: ", "")
                except:
                    quiz["correct_answer"] = correct_answer_option.replace("Explanation: ", "")
                # Add the completed quiz to the list of quizzes
                quizzes.append(quiz)
                # Reset the quiz dictionary for the next quiz
                quiz = {"options": []}

        # Store the quizzes in the session
        session['quizzes'] = quizzes

        # Initialize the quiz index and the score
        session['quiz_index'] = 0
        session['score'] = 0

    # If this is a GET request or the user has just answered a question
    if request.method == 'GET' or 'answer' in request.form:
        # If the user has just answered a question, check if the answer is correct
        if 'answer' in request.form:
            correct_answer = session['quizzes'][session['quiz_index']]['correct_answer']
            if request.form['answer'] in correct_answer:
                session['score'] += 1
                flash('Correct!', 'success')
            else:
                flash('Incorrect.', 'error')

            # Increment the quiz index
            session['quiz_index'] += 1

            # If there are no more quizzes, redirect the user to the score page
            if session['quiz_index'] >= len(session['quizzes']):
                return redirect(url_for('score'))

    if session['quiz_index'] < len(session['quizzes']):
                quiz = session['quizzes'][session['quiz_index']]

    else:
        flash('Sorry, there are no more quizzes. Try again later!', "error")
        return redirect(url_for('chat'))

    return render_template('quiz.html', quiz=quiz, message =get_flashed_messages())

@app.route('/chat/quiz_answer', methods=['POST'])
def quiz_answer():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if 'answer' in request.form:
        user_answer = request.form['answer']
        quiz = session['quizzes'][session['quiz_index']]
        correct_answer = quiz['correct_answer']
        user_session = UserSession.query.get(session['email'])
        user_session.quiz_count += 1  # Increment the quiz count
                    
        with open(session['quiz_file_path'], "a+") as f:
            
            f.write(f"{quiz['question']}\n")
            f.write(f"A. {quiz['A']}\n")
            f.write(f"B. {quiz['B']}\n")
            f.write(f"C. {quiz['C']}\n")
            f.write(f"D. {quiz['D']}\n")
            f.write(f"ANSWER: {quiz['correct_answer'].strip(',')[0]}\n\n")

        if user_answer in correct_answer:
            session['score'] += 1
            flash('Correct!', 'success')
            user_session.normalized_score += 10 / len(session['quizzes'])  # Update the normalized score
        else:
            flash('Incorrect.', 'error')
        db.session.commit()  # Don't forget to commit the changes

    # Increment the quiz index
    session['quiz_index'] += 1

    # If there are no more quizzes, redirect the user to the score page
    if session['quiz_index'] >= len(session['quizzes']):
        return redirect(url_for('score'))

    return redirect(url_for('quiz'))

@app.route('/chat/score')
def score():
    if 'email' not in session or 'score' not in session:
        return redirect(url_for('login'))

    return render_template('score.html', score=session['score'], quizzes=session['quizzes'])  # Send the quizzes to the frontend

@app.route('/chat/download_chat_history')
def download_chat_history():
    return send_from_directory('Users/'+session['email'], 'chat_history.json', as_attachment=True)

@app.route('/chat/download_quizzes')
def download_correct_answers():
    return send_from_directory('Users/'+session['email'], 'quiz.txt', as_attachment=True)

@app.route('/chat/download/<filename>')
def download(filename):
    return send_from_directory(session['email'], filename, as_attachment=True)


@app.route('/chat/logout')
def logout():
    session.pop('email', None)
    session.pop('conversation', None)
    session.pop('quizzes', None)  # Clear the quizzes
    # Don't reset the session count and last updated date
    return redirect(url_for('login'))

app.static_folder = 'static'

if __name__ == '__main__':
    app.run(debug=True, port=8000)