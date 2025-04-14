import os
import whisper
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from openai import OpenAI
import sys

# === Setup Flask ===
app = Flask(__name__, static_folder="static")
CORS(app)

# === Add AI_Assistant to Python Path for Importing ===
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI_Assistant/AI_Assistant')))

from ai_twin import process_input  # Now safely import process_input from ai_twin.py

# === OpenRouter Client Config ===
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

EXTRA_HEADERS = {
    "HTTP-Referer": "https://yourwebsite.com",
    "X-Title": "PersonaAI",
}

GEMINI_MODEL = "google/gemini-2.5-pro-exp-03-25:free"

# === Whisper Transcription Helper ===
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# === Route: Text or Audio Input to Voice Cloning Pipeline ===
@app.route('/api/voice', methods=['POST'])
def handle_voice_cloning():
    transcription = ""
    prompt = request.form.get("prompt", "").strip()
    mode = request.form.get("mode", "").strip()  # 'text' or 'audio'

    if mode == "audio":
        if "audio" not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        audio_file = request.files["audio"]
        audio_path = "temp_input.wav"
        audio_file.save(audio_path)
        transcription = transcribe_audio(audio_path)
        os.remove(audio_path)

    elif mode == "text":
        if not prompt:
            return jsonify({"error": "No text provided for 'text' mode"}), 400
        transcription = prompt

    else:
        return jsonify({"error": "Invalid mode. Choose either 'audio' or 'text'."}), 400

    try:
        result = process_input(transcription)  # This returns dict with 'path', 'text'
        audio_path = result["path"]
        file_name = os.path.basename(audio_path)

        # Move generated file to backend/static/audio
        static_audio_dir = os.path.join(app.root_path, "static", "audio")
        os.makedirs(static_audio_dir, exist_ok=True)

        final_audio_path = os.path.join(static_audio_dir, file_name)
        os.replace(audio_path, final_audio_path)

        audio_url = f"/static/audio/{file_name}"

        return jsonify({
            "transcription": result["text"],
            "audio_url": audio_url
        })
    except Exception as e:
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# === Serve Audio File if Direct Access Needed ===
@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory(os.path.join(app.root_path, 'static', 'audio'), filename)

# === Start Server ===
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
