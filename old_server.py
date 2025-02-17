from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline, Conversation

app = Flask(__name__)
CORS(app)

# Initialize the conversational pipeline with DialoGPT
chatbot = pipeline("conversational", model="microsoft/DialoGPT-medium")

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    
    if not user_message:
        return jsonify({"response": "Please provide a valid message."})
    
    # Create a conversation with the user's message
    conversation = Conversation(user_message)
    
    # Get the response from the conversation pipeline
    try:
        result = chatbot(conversation)
        # The conversation object now holds the history; extract the latest reply.
        response_text = result.generated_responses[-1]
    except Exception as e:
        response_text = f"Error generating response: {str(e)}"
    
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
