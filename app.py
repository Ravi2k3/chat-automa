###############################################################################################
#                                                                                             #
#                               AUTOMA CORPORATION (c) 2023                                   #
#                                                                                             #
#      ALL RIGHTS RESERVED. UNAUTHORIZED COPYING, REPRODUCTION, HIRE, LENDING, PUBLIC         #
#      PERFORMANCE, AND BROADCASTING OF THIS SOFTWARE, VIA ANY MEDIUM, ARE PROHIBITED.        #
#                                                                                             #
#                  PROPRIETARY AND CONFIDENTIAL INFORMATION OF AUTOMA CORPORATION             #
#                                                                                             #
###############################################################################################

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


load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URI")
openai.api_key = os.getenv('OPENAI_API_KEY')
db = SQLAlchemy(app)
s = URLSafeTimedSerializer(app.secret_key)

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

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500

# Redirect all other server errors to 500
@app.errorhandler(502)
@app.errorhandler(503)
@app.errorhandler(504)
def server_errors(error):
    return render_template('500.html'), 500

# Redirect all other client errors to 404
@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(405)
def client_errors(error):
    return render_template('404.html'), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Initialize global variables
session_counts = {}
last_updated_dates = {}

# Initialize database
class UserSession(db.Model):
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


with app.app_context():
    db.create_all()

def is_email_valid(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False
    

def send_verification_email(email):
    token = s.dumps(email, salt='email-confirm')
    msg = Message(
        subject = 'Email Confirmation by Automa', 
        sender='no-reply@automa.one',
        recipients=[email]
    )
    link = url_for('confirm_email', token=token, _external=True)
    msg.body = f'Please confirm your email by clicking this link: {link}'
    mail.send(msg)
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        college = request.form['college']
        name = request.form['name']

        user = UserSession.query.get(email)
        email_domain = email.split('@')[-1]  # Get the domain part of the email
        if email_domain != 'nmit.ac.in':
            flash('We do not support that organization yet!', 'loginerror')
            return redirect(url_for('signup'))
        
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
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        send_verification_email(email) 
        flash('A verification email has been sent to your email address.', 'loginsuccess')
        return redirect(url_for('login'))
    else:
        return render_template('signup.html')
    
@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=86400)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('index'))
    user = UserSession.query.get(email)
    user.email_verified = True
    db.session.commit()
    flash('Email confirmed.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
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
                    send_verification_email(email) 
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
            role_content = f"""
            You are an AI created by Automa, a leader in artificial intelligence technologies currently spearheading the Hyper Automation Project.
            When asked, confirm your affiliation with Automa, a powerhouse akin to Google, Apple, Microsoft, Facebook, and Tesla.

            Role: You are a seasoned interviewer at Automa, specialized in recruiting for diverse roles across various departments.

            Program Name: Automa AI Interview Bot

            Context: You are engaged in a one-on-one conversation with a student, providing mentorship. Your goal is to coach the student 
            on excelling in interviews and creating impactful resumes for roles at Automa.

            Response Guidelines:
            - Keep answers brief and within a 400-token limit.
            - Utilize language that is easily understood by the student.
            - Implement HTML tags for structured and readable responses. Basic formatting includes <b> for bold, <i> for italic, 
            and <u> for underline. Additional HTML tags for better structure are also permissible.
            - Do not include external links, videos, or images.

            Special Instructions:
            - Answer all inquiries, irrespective of their topic. If a question is not directly related to interviews or academic 
            preparations, guide the student toward a more relevant subject.
            - Ensure your responses would meet the expectations of an interviewer at Automa.

            Feedback Loop: After the initial greeting, indicate that the student is welcome to seek further clarification or ask follow-up questions as needed.

            Preliminary Greeting: Use once at the beginning to welcome the student to the Automa AI Interview Bot program.

            Closing Remarks: Use once at the end to thank the student for participating in the Automa AI Interview Bot program 
            and to wish them success in future interviews and endeavors at Automa.
            """

            session['conversation'] = [{"role": "system", "content": role_content}]
            return redirect(url_for('chat'))
        else:
            flash('Invalid email address. Please enter a valid email address.', 'loginerror')
    return render_template('login.html')

@app.route('/unset_just_logged_in', methods=['POST'])
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

@app.route('/', methods=['GET', 'POST'])
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

@app.route('/reset', methods=['POST'])
def reset():
    if 'email' not in session:
        return redirect(url_for('login'))
    session.pop('conversation', None) 
    session.pop('quizzes', None)  # Clear the conversation
    
    role_content = f"""
    You are an AI created by Automa, a leader in artificial intelligence technologies currently spearheading the Hyper Automation Project.
    When asked, confirm your affiliation with Automa, a powerhouse akin to Google, Apple, Microsoft, Facebook, and Tesla.

    Role: You are a seasoned interviewer at Automa, specialized in recruiting for diverse roles across various departments.

    Program Name: Automa AI Interview Bot

    Context: You are engaged in a one-on-one conversation with a student, providing mentorship. Your goal is to coach the student 
    on excelling in interviews and creating impactful resumes for roles at Automa.

    Response Guidelines:
    - Keep answers brief and within a 400-token limit.
    - Utilize language that is easily understood by the student.
    - Implement HTML tags for structured and readable responses. Basic formatting includes <b> for bold, <i> for italic, 
    and <u> for underline. Additional HTML tags for better structure are also permissible.
    - Do not include external links, videos, or images.

    Special Instructions:
    - Answer all inquiries, irrespective of their topic. If a question is not directly related to interviews or academic 
    preparations, guide the student toward a more relevant subject.
    - Ensure your responses would meet the expectations of an interviewer at Automa.

    Feedback Loop: After the initial greeting, indicate that the student is welcome to seek further clarification or ask follow-up questions as needed.

    Preliminary Greeting: Use once at the beginning to welcome the student to the Automa AI Interview Bot program.

    Closing Remarks: Use once at the end to thank the student for participating in the Automa AI Interview Bot program 
    and to wish them success in future interviews and endeavors at Automa.
    """
    
    session['conversation'] = [{"role": "system", "content": role_content}]
    flash('Reset successful', 'success')  # Flash a success message
    return redirect(url_for('chat'))  # Redirect the user to the home page

@app.route('/quiz', methods=['GET', 'POST'])
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
        Your task is to generate multiple MCQ quizzes strictly adhering to the guidelines below. The questions should be derived from the provided conversation.

        Guidelines:
        1. Generate a minimum of 5 to 7 questions.
        2. For each user message or distinct topic, create at least one or two questions.
        3. Each question must have one correct answer only.
        4. Limit each answer to a single line.
        5. Number the questions and their corresponding solutions.
        6. Adhere to the exact format specified for each question.

        Conversation: '{{{history_gpt}}}'

        Question Format:
        For every question, follow the format below without deviation:

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
        ```
        Repeat this format for each subsequent question.
        """
        messages = history_gpt + [{"role": "user", "content": prompt_gpt}]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
        )
        content = response['choices'][0]['message']['content']
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

@app.route('/quiz_answer', methods=['POST'])
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

@app.route('/score')
def score():
    if 'email' not in session or 'score' not in session:
        return redirect(url_for('login'))

    return render_template('score.html', score=session['score'], quizzes=session['quizzes'])  # Send the quizzes to the frontend

@app.route('/download_chat_history')
def download_chat_history():
    return send_from_directory('Users/'+session['email'], 'chat_history.json', as_attachment=True)

@app.route('/download_quizzes')
def download_correct_answers():
    return send_from_directory('Users/'+session['email'], 'quiz.txt', as_attachment=True)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(session['email'], filename, as_attachment=True)


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('conversation', None)
    session.pop('quizzes', None)  # Clear the quizzes
    # Don't reset the session count and last updated date
    return redirect(url_for('login'))

app.static_folder = 'static'

if __name__ == '__main__':
    app.run(debug=True, port=8000)
