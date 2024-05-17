import os
import re
import speech_recognition as sr
from googletrans import Translator

# Function to translate text to English using Google Translate API
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

# Main function to process the audio file
def process_audio_and_translate():
    recognizer = sr.Recognizer()
    audio_file_path = "E:/key_sonnet/final model/io/courage.aiff"
    
    with sr.AudioFile(audio_file_path) as source:
        recorded_audio = recognizer.listen(source)
        print("Done recording")
    
    try:
        print("Recognizing the text")
        text = recognizer.recognize_google(recorded_audio, language="en-US")
        print("Decoded Text : {}".format(text))
        
        # Save the recognized text to a file
        base_name = os.path.splitext(audio_file_path)[0]
        english_file_path = base_name + ".txt"
        with open(english_file_path, "w") as f:
            f.write(text)
        print("English text saved to {}".format(english_file_path))
        
        # Translate the English text to Bengali
        bengali_text = translate_to_bengali(text)
        filtered_bengali_text = filter_garbage(bengali_text)
        
        # Save the translated and filtered Bengali text to a file
        bengali_file_path = base_name + "_bn.txt"
        with open(bengali_file_path, "w", encoding='utf-8') as f:
            f.write(filtered_bengali_text)
        print("Bengali text saved to {}".format(bengali_file_path))
        
    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    process_audio_and_translate()