# ACS-Learning

This repository contains the code for a chat system. The chat system allows users to ask questions and receive answers from an AI-powered chatbot. It also includes features such as user authentication, session management, and quizzes.

## Features

- User authentication: Users can log in using their email addresses.
- Session management: The system keeps track of the number of sessions and messages for each user.
- AI-powered chatbot: Users can ask questions and receive answers from an AI chatbot powered by OpenAI's GPT-3.5 Turbo model.
- Quizzes: Users can take quizzes generated based on the conversation with the chatbot.
- Chat history: The system stores the chat history for each user.
- Error handling: The system handles errors and displays appropriate error messages to the users.

## Prerequisites

Before running the code, make sure you have the following dependencies installed:

- Flask
- email_validator
- openai
- Flask SQLAlchemy
- dotenv
- BeautifulSoup
- Gunicorn
- Werkzeug

## Configuration

The application requires some configuration variables to be set. Please follow the steps below to set up the configuration:

1. Create a `.env` file in the root directory of the project.
2. Set the following environment variables in the `.env` file:

   - `SECRET_KEY`: A secret key for the Flask application.
   - `OPENAI_API_KEY`: Your OpenAI API key.
   - `DATABASE_URL`: The URL for the database.

3. Save the `.env` file.

## Usage

To run the application, follow the steps below:

1. Install the required dependencies by running the following command:

   ```
   pip install flask email_validator openai flask_sqlalchemy python-dotenv beautifulsoup4 gunicorn Werkzeug && sudo apt-get install gunicorn
   ```

2. Clone the repository:

   ```
   git clone https://github.com/ecstra/ACS-Learning.git
   ```

3. Change the directory to the cloned repository:

   ```
   cd ACS-Learning
   ```

4. Create a `.env` file in the root directory of the project.

5. Set the following environment variables in the `.env` file:

   ```
   SECRET_KEY=<your_secret_key>
   OPENAI_API_KEY=<your_openai_api_key>
   DATABASE_URL=<your_database_url>
   ```

   Replace `<your_secret_key>`, `<your_openai_api_key>`, and `<your_database_url>` with your own values.

6. Save the `.env` file.

7. Start the application using Gunicorn:

   ```
   gunicorn -w 4 -b 127.0.0.1:5000 chat_system:app
   ```

   The application will start running on `http://127.0.0.1:5000/`.

## Routes

The application provides the following routes:

- `/login`: Allows users to log in.
- `/logout`: Logs out the user and redirects to the login page.
- `/`: The main chat interface where users can ask questions and receive answers.
- `/quiz`: Allows users to take quizzes based on the conversation.
- `/score`: Shows the user's score after completing the quizzes.
- `/download_chat_history`: Allows users to download their chat history.
- `/download_quizzes`: Allows users to download the correct answers for the quizzes.

## Error Handling

The application handles the following errors:

- 404: Page not found.
- 500: Internal server error.
- Other exceptions: Generic error message.

## Disclaimer

Please note that unauthorized copying of this code is strictly prohibited. This code is proprietary and confidential.

If you have any questions or need further assistance, please feel free to contact us.

## License
This project is licensed under the [Automa Proprietary License Agreement](LICENSE) license. Please see the [LICENSE](LICENSE) file for more details.
