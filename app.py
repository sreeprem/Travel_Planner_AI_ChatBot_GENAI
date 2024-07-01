from flask import Flask, request, jsonify, session
from flask_session import Session
import openai

app = Flask(__name__, static_url_path='', static_folder='static')

# Configure Flask Session
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Set up OpenAI API key
openai.api_key = 'removed for security reasons and billing purposes'

# Predefined questions
questions = [
    "What is your destination?",
    "How many days are you planning to travel?",
    "What is your budget?"
]

# Function to validate answers
def validate_answers(answers):
    # Add your validation logic here
    return True

# Function to suggest plans
def suggest_plans(answers):
    # Convert answers to a string
    answers_str = ' '.join(answers)

    # Ask a question to OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": answers_str}
        ]
    )

    # Get the model's message from the response
    model_message = response['choices'][0]['message']['content']

    return model_message

# Serve the HTML file for the frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Endpoint for handling user queries
@app.route('/query', methods=['POST'])
def handle_query():
    # Get user query from the request
    user_query = request.json['query']

    # Start asking questions after receiving the "start" command
    if user_query.lower() == "start":
        # Reset session variables
        session['answers'] = []
        session['question_index'] = 0

        recommendation = questions[session['question_index']]
    elif 'answers' in session and 'question_index' in session and session['question_index'] < len(questions):
        # Add user query to answers
        session['answers'].append(user_query)

        # Increment question index
        session['question_index'] += 1

        # If there are more questions, ask the next question
        if session['question_index'] < len(questions):
            recommendation = questions[session['question_index']]
        else:
            # If all questions have been asked, process answers with OpenAI
            if validate_answers(session['answers']):
                recommendation = suggest_plans(session['answers'])
            else:
                recommendation = "Sorry, I didn't understand your answers. Could you please provide more details?"
    else:
        recommendation = "Please type 'start' to begin planning your travel."

    # Return recommendation as JSON response
    return jsonify({'recommendation': recommendation})

if __name__ == '__main__':
    app.run(debug=True)