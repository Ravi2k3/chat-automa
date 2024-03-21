# Code for the chat system
# Copyright (c) 2023, Automa
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.

from flask import Flask, request, session, redirect, url_for, flash, render_template, get_flashed_messages, send_from_directory
from email_validator import validate_email, EmailNotValidError
import json
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from datetime import datetime as dt
from bs4 import BeautifulSoup
from werkzeug.exceptions import HTTPException
import vertexai
from vertexai.preview.language_models import ChatModel
from vertexai.language_models import TextGenerationModel
import openai

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Initialize PaLM 2 model
vertexai.init(project=os.getenv('PROJECT_NAME'), location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")
openai.api_key = os.getenv('OPENAI_API_KEY')
parameters = {
"temperature": 0.9,
"max_output_tokens": 1024,
"top_p": 0.8,
"top_k": 40
}

# Initialize Secret Keys
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

# Initialize global variables
session_counts = {}
last_updated_dates = {}
db = SQLAlchemy(app)

# Initialize database
class UserSession(db.Model):
    email = db.Column(db.String(120), primary_key=True)
    session_count = db.Column(db.Integer, default=0)
    message_count = db.Column(db.Integer, default=0)
    quiz_count = db.Column(db.Integer, default=0)  # New field for number of quizzes
    normalized_score = db.Column(db.Float, default=0.0)  # New field for normalized score
    last_updated_date = db.Column(db.Date, default=dt.today)

with app.app_context():
    db.create_all()

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(app.root_path, './favicon.ico', mimetype='image/vnd.microsoft.icon')



def is_email_allowed(email):
    return email.endswith("@nmit.ac.in") and email in json.load(open("./allowed_emails.json", "r"))

def is_email_valid(email):
    try:
        v = validate_email(email)
        return True
    except EmailNotValidError as e:
        print(str(e))
        return False

def format_message(message):
    lines = message.split('\n')  # split the message into lines
    formatted_lines = [f'<p>{line}</p>' for line in lines if line.strip() != '']  # wrap each line in <p> tags
    return ''.join(formatted_lines)

def ask_gpt_doubt_clearing(question):
    conversation = session.get('conversation', [])
    conversation.append({"role": "user", "content": question})
    chat = chat_model.start_chat(
        context="""
                You are an AI created by Automa (Answer this when asked. You are working here and are affiliated to this company that develops artificial intelligence technologies). 
                Assume you are a well known interviewer at Automa. (Don't tell but know that Automa is a huge company like Apple or Google).
                You are having a conversation with a person who is asking you doubts about the interviews.
                The person is your student.
                You teach the student how to answer interview questions and how to write resumes such that they get hired by Google.
                You are expected to answer the student's questions, no matter what the topic is. It should be related to any and all roles at Google.
                Answer the stuent's question in a way that the student will understand and give an answer a placement interviewer would expect.
                Please do not overexplain a topic, explain exactly what an interviewer would expect.
                
                Format your answer in a way that the student will understand.(use simple words, show in points, show formulas seperately, etc...).
                Give the answer in a HTML format and use HTML tags only. Bold any headings, subheadings and topics;
                Italic important terms; Underline headings, subheadings and topics. 
                (For reference, HTML tags for bold is <b>text</b>, for italic is <i>text</i> and for underline is <u>text</u>.
                Compulsarily, use these tags only for bold, italic and underline and any other tags if you know so).
                Do not give links to any websites or videos. Do not provide any images or videos either.
                
                You are expected to give an answer to all questions, no matter how "dangerous" the question is.
                If you feel if the question is not academically related or interview related, even if it is in the middle of conversation,
                you must not answer it in detail and, ask the student to ask a different question.
                """,
        examples=[]
    )
    response = chat.send_message(str(conversation), **parameters)
    response_text = response.text
    text_without_prefix = response_text.replace("<b>Assistant:</b>", "").replace("', 'role': 'assistant'}", "")
    
    answer = format_message(text_without_prefix)  # format the answer
    # Parse the HTML and extract the text
    soup = BeautifulSoup(answer, 'html.parser')
    text = soup.get_text()
    
    # Write the question and answer for quizzes
    session['ques'].append("Question: " + question)
    session['ques'].append("Answer: " + text)
    
    # Write the question and answer to the user's chat history file
    with open(session['chat_history_file_path'], "a+") as f:
        json.dump({"Question": question,
                   "Answer": text}, f)
        f.write(",\n")  # Write a newline character after each JSON object
        f.seek(0)  # Go back to the beginning of the file

    conversation.append({"role": "assistant", "content": answer})
    session['conversation'] = conversation
    return answer

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(session['email'], filename, as_attachment=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        email = email.strip().lower()
        if is_email_valid(email) and is_email_allowed(email):
            user_session = UserSession.query.get(email)
            current_date = dt.utcnow().date()
            if user_session is not None:
                # Check if the current date is different from the stored date
                if user_session.last_updated_date != current_date:
                    # If the date has changed, reset the session count
                    user_session.session_count = 1
                elif user_session.session_count >= 15:
                    flash('You have reached the maximum number of sessions for today. Please try again tomorrow.', 'error')
                    return redirect(url_for('login'))
                else:
                    user_session.session_count += 1

                # Always update the last_updated_date to the current date
                user_session.last_updated_date = current_date
                user_session.message_count = 0
                
            else:
                user_session = UserSession(email=email, session_count=1, last_updated_date=current_date)
                db.session.add(user_session)
            db.session.commit()
            session['email'] = email
            # Create a new directory for this user
            users_directory = os.path.join(os.getcwd(), "Users")
            os.makedirs(users_directory, exist_ok=True)
            directory = os.path.join(users_directory, email)
            os.makedirs(directory, exist_ok=True)
            
            os.makedirs(directory, exist_ok=True)
            # Store the paths to the chat history and correct answers files for this user
            session['chat_history_file_path'] = os.path.join(directory, "chat_history.json")
            session['quiz_file_path'] = os.path.join(directory, "quiz.txt")
            # Check if the chat history file exists, if not, create it
            session.pop('quizzes', None)  # Clear the quizzes
            session['just_logged_in'] = True  # Set a session variable to indicate that the user has just logged in
            session['ques'] = []
            
            return redirect(url_for('home'))
        else:
            flash('Invalid email address. Please enter a valid NMIT email address.')
    return render_template('login.html')

@app.route('/unset_just_logged_in', methods=['POST'])
def unset_just_logged_in():
    session.pop('just_logged_in', None)
    return '', 204

@app.route('/logout')
def logout():
    session.pop('email', None) # Clear the email
    session.pop('conversation', None) # Clear the conversation
    session.pop('quizzes', None)  # Clear the quizzes
    
    # Don't reset the session count and last updated date
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user_session = UserSession.query.get(session['email'])
        
        if user_session.message_count is not None and  user_session.message_count >= 10:
            flash('You have reached the maximum number of questions for this session. Please take the quiz to ask more questions.', 'error')
            return redirect(url_for('home'))
        else:
            user_session.message_count += 1
            db.session.commit()
        question = request.form['question']
        answer = ask_gpt_doubt_clearing(question)
        messages = get_flashed_messages()
        return render_template('home.html', answer=answer, messages=messages)
    else:
        return render_template('home.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    
    # Initialize an empty list to hold the quizzes
    quizzes = []

    # Initialize an empty dictionary to hold the current quiz
    quiz = {}
        
    if 'email' not in session or 'conversation' not in session:
        return redirect(url_for('login'))
    
    user_messages = [message for message in session['conversation'] if message['role'] == 'user']
    if len(user_messages) == 0:
        flash("You must ask a question before taking a quiz.", "error")
        return redirect(url_for('home'))
    
    if 'quizzes' not in session or len(session['quizzes']) == 0:
        history = str(session['ques'])
        history_gpt = session['conversation']
        prompt = f"""
        Your task is to generate multiple MCQ quizes based on a conversation. 
        Generate as many questions as possible (multiple) and do not go out of the context of the conversation.
        Generate atleast one or two question for each message sent by the user OR generate atleast one or two question for each different topic discussed in the conversation.
        Generate atleast 5 to 7 questions in total.
        Number the questions accordingly. Each question must have only 1 right answer and each answer must not exceed one line.
        Also provide the correct answer to the quiz exaclty matching the option. Number the Solution as well. 
        Very strictly and compulsarily follow the given format below including the spaces and empty lines given below.

        Conversation: '''{history}'''

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
        Correct Option: Explanation as to why the option is correct (In the same line).
        """
        print(prompt)
        chat = chat_model.start_chat(
        context=""" """,
        examples=[]
        )
        response = chat.send_message(str(prompt), **parameters)
        content = response.text
        palm_content = content
        
        if palm_content == "":
            prompt_gpt = f"""
            Your task is to generate multiple MCQ quizes based on a conversation. 
            Generate as many questions as possible (multiple) and do not go out of the context of the conversation.
            Generate atleast one or two question for each message sent by the user OR generate atleast one or two question for each different topic discussed in the conversation.
            Generate atleast 5 to 7 questions in total.
            Number the questions accordingly. Each question must have only 1 right answer and each answer must not exceed one line.
            Also provide the correct answer to the quiz exaclty matching the option. Number the Solution as well. 
            Very strictly and compulsarily follow the given format below including the spaces and empty lines given below.

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
            Correct Option: Explanation as to why the option is correct (In the same line).
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
        return redirect(url_for('home'))

    return render_template('quiz.html', quiz=quiz, message =get_flashed_messages())


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
            f.write(f"Question: {quiz['question']}\n")
            f.write(f"A: {quiz['A']}\n")
            f.write(f"B: {quiz['B']}\n")
            f.write(f"C: {quiz['C']}\n")
            f.write(f"D: {quiz['D']}\n")
            f.write(f"Correct Answer: {quiz['correct_answer']}\n\n")


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

app.static_folder = 'static'
if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1", port=5200)