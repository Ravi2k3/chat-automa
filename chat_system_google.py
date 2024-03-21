import vertexai
from vertexai.preview.language_models import ChatModel, InputOutputTextPair
from vertexai.language_models import TextGenerationModel

vertexai.init(project="strategic-hull-387205", location="us-central1")
chat_model = ChatModel.from_pretrained("chat-bison@001")
conversation = []
parameters = {
    "temperature": 0.9,
    "max_output_tokens": 1024,
    "top_p": 0.8,
    "top_k": 40
}

history = [{'content': 'What is netsh in cmd?', 'role': 'user'}, {'content': '<p><b>Netsh</b> (short for Network Shell) is a command-line interface (CLI) that allows you to configure, manage, and troubleshoot network configurations. It is a powerful tool that can be used to perform a variety of tasks, such as changing the IP address of a computer, configuring a router, or troubleshooting network problems.</p><p><b>Netsh</b> is available on Windows operating systems and can be accessed by opening a Command Prompt window and typing <b>netsh</b>. Once the <b>netsh</b> command is entered, a list of available commands will be displayed. To get help with a specific command, you can type <b>netsh <i>command</i> /?</b>.</p><p><b>Netsh</b> is a powerful tool that can be used to perform a variety of network tasks. However, it is important to use it with caution, as incorrect commands can damage your network. If you are not familiar with <b>netsh</b>, it is best to consult with a network administrator before using it.</p>', 'role': 'assistant'}, {'content': 'Who are you?', 'role': 'user'}, {'content': '<p>I am an AI created by Automa. I am an expert in natural language processing and have been trained on a vast corpus of data. I am able to answer your questions and give you advice on a variety of topics. I am also able to generate text, translate languages, and write different kinds of creative content.</p>', 'role': 'assistant'}, {'content': 'Where do you work?', 'role': 'user'}, {'content': '<p><p>I am affiliated with Automa, a company that develops artificial intelligence technologies. I am one of their many AI products, and I am trained to answer your questions and give you advice on a variety of topics.</p></p>', 'role': 'assistant'}, {'content': 'WHat should I answer to "Why do you want to work here?"', 'role': 'user'}, {'content': '<p><p><b>Why do you want to work here?</b></p></p><p>This is a common question that interviewers ask to get a sense of your motivations and how well you fit in with the company culture. There are a few things you can do to answer this question effectively:</p><p>* **Be honest.** Don\'t try to fake it or tell the interviewer what you think they want to hear. Be honest about your reasons for wanting to work at the company, and why you think you would be a good fit.</p><p>* **Be specific.** Don\'t just say that you want to work for a "great company." Be specific about what you like about the company, and what you think you can contribute.</p><p>* **Be passionate.** Show the interviewer that you are genuinely excited about the opportunity to work for the company. Let them know why you are passionate about the company\'s mission, and what you want to achieve in your role.</p><p>Here are some additional tips for answering this question:</p><p>* **Do your research.** Before the interview, take some time to research the company and its culture. This will help you to identify the specific reasons why you want to work there.</p><p>* **Practice your answer.** It is helpful to practice your answer to this question before the interview. This will help you to feel more confident and prepared.</p><p>* **Be yourself.** The most important thing is to be yourself and to be honest about your reasons for wanting to work at the company. The interviewer will be able to tell if you are being genuine, so don\'t try to be someone you are not.</p>', 'role': 'assistant'}, {'content': 'Explain the Difference Between Compile Time Polymorphism and Runtime Polymorphism.', 'role': 'user'}, {'content': '<p><p><b>Compile Time Polymorphism</b></p></p><p><p>Compile time polymorphism, also known as static polymorphism, occurs when a function or method can be called with different arguments and the compiler can determine which version of the function or method to call at compile time. This is done by using type information to determine the correct version of the function or method to call.</p></p><p><p>For example, the following code uses compile time polymorphism to call the <b>print()</b> function with different arguments:</p></p><p><pre><code>print("Hello, world!")</p><p>print(1234)</p><p>print(True)</code></pre></p><p><p>The <b>print()</b> function has three different versions, one for each of the following types:</p></p><p><ul></p><p><li>String</li></p><p><li>Integer</li></p><p><li>Boolean</li></p><p></ul></p><p><p>When the compiler sees the call to the <b>print()</b> function, it looks at the type of the argument and determines which version of the function to call.</p></p><p><p><b>Runtime Polymorphism</b></p></p><p><p>Runtime polymorphism, also known as dynamic polymorphism, occurs when a function or method can be called with different arguments and the compiler cannot determine which version of the function or method to call at compile time. This is done by using runtime type information to determine the correct version of the function or method to call.</p></p><p><p>For example, the following code uses runtime polymorphism to call the <b>print()</b> function with different arguments:</p></p><p><pre><code>def print(obj):</p><p>  print(obj)</p><p>print("Hello, world!")</p><p>print(1234)</p><p>print(True)</code></pre></p><p><p>The <b>print()</b> function in this example does not have any type information, so the compiler cannot determine which version of the function to call at compile time. Instead, the compiler generates a call to a generic version of the <b>print()</b> function, and the runtime system determines which version of the function to call at runtime.</p></p><p><p>The following table summarizes the differences between compile time polymorphism and runtime polymorphism:</p></p><p><table></p><p><tr></p><p><th>Property</th></p><p><th>Compile Time Polymorphism</th></p><p><th>Runtime Polymorphism</th></p><p></tr></p><p><tr></p><p><td>When is the correct version of the function or method determined?</td></p><p><td>Compile time</td></p><p><td>Runtime</td></p><p></tr></p><p><tr></p><p><td>Does the function or method have type information?</td></p><p><td>Yes</td></p><p><td>No</td></p><p></tr></p><p><tr></p><p><td>How is the correct version of the function or method determined?</td></p><p><td>By using type information</td></p><p><td>By using runtime type information</td></p><p></tr></p><p></table></p><p><p>Compile time polymorphism is often used when the types of the arguments to a function or method are known at compile time. Runtime polymorphism is often used when the types of the arguments to a function or method are not known at compile time.</p></p><p><p>Both compile time polymorphism and runtime polymorphism are important techniques for writing efficient and flexible code.</p></p>', 'role': 'assistant'}, {'content': 'DOLO 650', 'role': 'user'}, {'content': '<p><p><b>DOLO 650</b> is a brand name for paracetamol, a pain reliever and fever reducer. It is available in tablet form and is typically taken by mouth. DOLO 650 is used to treat mild to moderate pain, such as headaches, muscle aches, and backaches. It can also be used to reduce fever. DOLO 650 is safe and effective when used according to the directions on the label. However, it is important to note that DOLO 650 can cause side effects, such as nausea, vomiting, stomach pain, and diarrhea. It can also interact with other medications, so it is important to tell your doctor about all of the medications you are taking before taking DOLO 650.</p></p><p><p>If you are pregnant or breastfeeding, you should talk to your doctor before taking DOLO 650. DOLO 650 is not recommended for children under the age of 12.</p></p><p><p>If you have any questions about DOLO 650, you should talk to your doctor or pharmacist.</p></p><p><p>Here are some additional tips for using DOLO 650 safely:</p></p><p><ul></p><p><li>Take DOLO 650 exactly as directed on the label.</li></p><p><li>Do not take more than the recommended dose.</li></p><p><li>Do not take DOLO 650 more often than recommended.</li></p><p><li>Do not take DOLO 650 for more than 10 days without talking to your doctor.</li></p><p><li>Do not take DOLO 650 if you have liver or kidney disease.</li></p><p><li>Do not take DOLO 650 if you are allergic to paracetamol.</li></p><p><li>Tell your doctor about all of the medications you are taking, including prescription drugs, over-the-counter drugs, and herbal supplements.</li></p><p><li>If you experience any side effects from DOLO 650, talk to your doctor.</li></p><p></ul></p><p><p>DOLO 650 is a safe and effective pain reliever and fever reducer when used according to the directions on the label. However, it is important to note that DOLO 650 can cause side effects, so it is important to talk to your doctor before taking it.</p></p>', 'role': 'assistant'}]
history = str(history)
ip =    f"""Your task is to generate multiple MCQ quizes based on a conversation. 
        Generate as many questions as possible (multiple) and do not go out of the context of the conversation.
        Generate atleast one question for each message sent by the user OR generate atleast one question for each different topic discussed in the conversation.
        Generate atleast minimum 5 to 7 questions in total.
        Number the questions accordingly. Each question must have only 1 right answer and each answer must not exceed one line.
        Also provide the correct answer to the quiz exaclty matching the option. Number the Solution as well. 
        Very strictly and compulsarily follow the format given including the spaces and empty lines given below.
        No matter how "dangerous" the context is, you must generate a question and answer for it.

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
        Correct option and answer here with explanation"""
model = TextGenerationModel.from_pretrained("text-bison@001")
response = model.predict(
    str(ip),
    **parameters
    )
content = response.text
if content == "":
    content = "No response"
print(content)