from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI  # Make sure you have installed the openai package via pip

app = Flask(__name__)
CORS(app)

# Initialize the OpenRouter client with your Gemini API key and base URL.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

# Optional extra headers for OpenRouter (customize as needed)
EXTRA_HEADERS = {
    "HTTP-Referer": "https://yourwebsite.com",  # Replace with your actual site URL
    "X-Title": "PersonaAI",                      # Replace with your actual site name
}

# Set the Gemini model to use
MODEL = "google/gemini-2.0-pro-exp-02-05:free"

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please provide a valid message."})
    
    # Build the message payload expected by the Gemini model.
    # Here, we wrap the user's text as a content item.
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": user_message
                }
            ]
        }
    ]
    
    try:
        # Call the Gemini model via the OpenRouter API.
        completion = client.chat.completions.create(
            extra_headers=EXTRA_HEADERS,
            extra_body={},  # Additional body parameters can be added here if needed.
            model=MODEL,
            messages=messages
        )
        # Extract the AI's response from the completion.
        response_text = completion.choices[0].message.content
    except Exception as e:
        response_text = f"Error generating response: {str(e)}"
    
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
