import os
import io
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import speech_recognition as sr
from googletrans import Translator
import re

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(app.root_path, 'io')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Function to translate text to Bengali using Google Translate API
def translate_to_bengali(text):
    translator = Translator()
    try:
        translated = translator.translate(text, src='auto', dest='bn')
        return translated.text
    except Exception as e:
        print(f"Error translating text: {e}")
        return ""

# Function to filter out garbage characters like URLs, emails, etc.
def filter_garbage(text):
    text = re.sub(r'http\S+|www.\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'\d+', '', text)
    return text

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Run the ffmpeg command
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.aiff')
        if os.path.exists(output_path):
            os.remove(output_path)
        command = ['ffmpeg', '-i', file_path, '-c:a', 'pcm_s16be', output_path]
        subprocess.run(command, check=True)
        file_path = output_path

        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            recorded_audio = recognizer.listen(source)
            print("Done recording")
        
        try:
            print("Recognizing the text")
            text = recognizer.recognize_google(recorded_audio, language="en-US")
            print("Decoded Text : {}".format(text))
            
            # Translate the English text to Bengali
            bengali_text = translate_to_bengali(text)
            filtered_bengali_text = filter_garbage(bengali_text)
            
            return jsonify({"english_text": text, "bengali_text": filtered_bengali_text}), 200
        
        except Exception as ex:
            return jsonify({"error": str(ex)}), 500

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('frontend', path)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
