# ACS-Learning

This repository contains the code for a chat system. The chat system allows users to ask questions and receive answers from an AI-powered chatbot. It also includes features such as user authentication, session management, and quizzes.

## Features

- User authentication: Users can log in using their email addresses.                                                                                                  [ ]
- Session management: The system keeps track of the number of sessions and messages for each user.
- AI-powered chatbot: Users can ask questions and receive answers from an AI chatbot powered by OpenAI's GPT-3.5 Turbo model.
- Quizzes: Users can take quizzes generated based on the conversation with the chatbot.
- Chat history: The system stores the chat history for each user.
- Error handling: The system handles errors and displays appropriate error messages to the users.

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

## To-Do

This is the todo for the next 1 month:

- Learn the code base.
- Learn about Gemini API.
- Learn React and RESTApi.
- Shift from OpenAI to Gemini 1.5 pro.
- Implement the buttons for images, check for camera access from browser or access from files.
- Implement Ctrl+V for pasting images from clipboard or copied images.
- Implement drag and drop for files, including code (all types, py, cpp, c, cu, md, etc..), PDFs. 
- AppRoute to process files either to 1.5-pro or 1.5 Vision.
- If possible replicate real time generation (token by token).
- React conversion of HTML and CSS.
- Enhance the propmts, change the Chain of Thoughts to match what the Gemini API expects.
- Try implementation of RAG for unlimited context (If possible).

## To-Do for Interview Bot

- Implement a placeholder for QnA, make it such that if we plug in whatever is given by CDC, it should work.
- Data augment the given questions to a dictionary that has appropriate depth (questions["sofware-engineer"]["aptitude"]).
- Make a new tab for the question answer part (test).
- Give them options for positions, ie, software engineer, full stack, etc.. 
- This will have topics for technical, interview, aptitude, whatever they give in the question bank.
- Make the bot generate whatever it seems necessary along with the questions in the database.
- Create a front end page to display results for the applicants. Show right answer and wrong answer.
- Add a button for more explanation that gets another response from the bot.
- Find a way to integrate an IDE and make it accessible or make llm decide if the code is correct or not and return a score.
- Commit to main. 
