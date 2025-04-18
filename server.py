import os
import whisper
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import sys

# Extend path for custom module import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../AI_Assistant')))
from AI_Assistant.clone_voice import transcribe, synthesize

app = Flask(__name__)
CORS(app)

# Reference to Gemini/OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

EXTRA_HEADERS = {
    "HTTP-Referer": "https://yourwebsite.com",
    "X-Title": "PersonaAI",
}

GEMINI_MODEL = "google/gemini-2.0-flash-lite-001"

# ========== GEMINI TEXT CHAT ==========
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"response": "Please provide a valid message."}), 400

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": user_message}]
    }]
    try:
        completion = client.chat.completions.create(
            extra_headers=EXTRA_HEADERS,
            extra_body={},
            model=GEMINI_MODEL,
            messages=messages
        )
        response_text = completion.choices[0].message.content
    except Exception as e:
        response_text = f"Error generating response: {str(e)}"

    return jsonify({"response": response_text})

# ========== TRANSCRIBE AUDIO ==========
def transcribe_audio(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

# ========== AUDIO + GEMINI CHAT ==========
@app.route('/api/audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    temp_audio_path = "temp_audio.wav"
    audio_file.save(temp_audio_path)

    try:
        transcription = transcribe_audio(temp_audio_path)
        os.remove(temp_audio_path)
    except Exception as e:
        return jsonify({"error": f"Error in transcription: {str(e)}"}), 500

    prompt_text = request.form.get('prompt', '').strip()
    combined_prompt = f"Audio transcription: {transcription}\nUser prompt: {prompt_text}" if prompt_text else f"Audio transcription: {transcription}"

    messages = [{
        "role": "user",
        "content": [{"type": "text", "text": combined_prompt}]
    }]
    try:
        completion = client.chat.completions.create(
            extra_headers=EXTRA_HEADERS,
            extra_body={},
            model=GEMINI_MODEL,
            messages=messages
        )
        generated_response = completion.choices[0].message.content
    except Exception as e:
        generated_response = f"Error generating response: {str(e)}"

    return jsonify({
        "transcription": transcription,
        "response": generated_response
    })

# ========== VOICE CLONING FROM AUDIO ==========
@app.route('/api/clone-audio', methods=['POST'])
def clone_from_audio():
  if 'audio' not in request.files:
    return jsonify({"error": "No audio file provided"}), 400

  audio_file = request.files['audio']
  original_filename = audio_file.filename
  file_ext = original_filename.split('.')[-1].lower()
  temp_audio_path = f"temp_input.{file_ext}"
  audio_file.save(temp_audio_path)

  try:
    # Save current working directory
    original_cwd = os.getcwd()

    # Build absolute path to base_dir
    current_dir = os.path.abspath(os.path.dirname(__file__))
    base_dir = os.path.join(current_dir, "..", "AI_Assistant", "AI_Assistant")
    ref_wav = os.path.join(base_dir, "rahul_voice.wav")
    output_path = os.path.join(base_dir, "generated_reply.wav")

    print(f"Received audio for transcription and voice cloning.")

    # Transcribe using proper file extension
    transcription = transcribe(temp_audio_path)
    print(f"Transcription: {transcription}")

    # Generate cloned voice
    synthesize(transcription, reference_audio=ref_wav)

    if not os.path.exists(output_path):
      raise FileNotFoundError(f"Output file not found at {output_path}")

    # Clean up temp file
    os.remove(temp_audio_path)

    return send_file(output_path, mimetype="audio/wav")

  except Exception as e:
    print(f"Error in clone_from_audio: {str(e)}")
    return jsonify({"error": f"Failed to generate cloned voice: {str(e)}"}), 500

    
# ========== VOICE CLONING FROM TEXT ==========
@app.route('/api/clone-text', methods=['POST'])
def clone_from_text():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        print(f"Received text for voice cloning: {text}")

        # Build absolute path to base_dir
        current_dir = os.path.abspath(os.path.dirname(__file__))
        base_dir = os.path.join(current_dir, "..", "AI_Assistant", "AI_Assistant")
        ref_wav = os.path.join(base_dir, "rahul_voice.wav")
        output_path = os.path.join(base_dir, "generated_reply.wav")

        print(f"Reference WAV: {ref_wav}")
        print(f"Output path: {output_path}")

        # Generate voice
        synthesize(text, reference_audio=ref_wav)

        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Output file not found at {output_path}")

        return send_file(output_path, mimetype="audio/wav")

    except Exception as e:
        print(f"Error in clone_from_text: {str(e)}")
        return jsonify({"error": f"Failed to generate cloned voice: {str(e)}"}), 500

# ========== START FLASK ==========
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
