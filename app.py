from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator, exceptions
from werkzeug.utils import secure_filename
import os
import logging
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB limit
app.secret_key = 'your-secret-key-here'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

translator = GoogleTranslator(source='auto', target='en')
SUPPORTED_LANGUAGES = translator.get_supported_languages(as_dict=True)
DEFAULT_SRC_LANG = 'auto'
DEFAULT_DEST_LANG = 'en'

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    input_text = ""
    src_lang = DEFAULT_SRC_LANG
    dest_lang = DEFAULT_DEST_LANG
    error = None
    char_count = 0
    
    if request.method == "POST":
        input_text = request.form.get("text", "")
        src_lang = request.form.get("src_lang", DEFAULT_SRC_LANG)
        dest_lang = request.form.get("dest_lang", DEFAULT_DEST_LANG)
        char_count = len(input_text)
        
        try:
            if not input_text.strip():
                raise ValueError("Please enter text to translate")
                
            if char_count > 5000:
                raise ValueError("Text exceeds maximum length of 5000 characters")
                
            translated_text = GoogleTranslator(
                source=src_lang, 
                target=dest_lang
            ).translate(input_text)
            
            # Log successful translations (without user data)
            logger.info(f"Translation successful: {src_lang}->{dest_lang}, {char_count} chars")
            
        except exceptions.LanguageNotSupportedException as e:
            error = f"Language not supported: {str(e)}"
            logger.error(f"Language error: {str(e)}")
        except exceptions.TranslationNotFound as e:
            error = "Translation not found. Please try different text."
            logger.error(f"Translation not found: {input_text[:50]}...")
        except Exception as e:
            error = f"Translation error: {str(e)}"
            logger.error(f"Translation error: {str(e)}")

    return render_template(
        "index.html",
        translated_text=translated_text,
        input_text=input_text,
        languages=SUPPORTED_LANGUAGES,
        src_lang=src_lang,
        dest_lang=dest_lang,
        error=error,
        char_count=char_count,
        max_chars=5000
    )

@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    text = data.get("text", "")
    src_lang = data.get("src_lang", DEFAULT_SRC_LANG)
    dest_lang = data.get("dest_lang", DEFAULT_DEST_LANG)
    
    if not text.strip():
        return jsonify({"error": "No text to translate"}), 400
        
    try:
        translated_text = GoogleTranslator(
            source=src_lang, 
            target=dest_lang
        ).translate(text)
        
        return jsonify({
            "translatedText": translated_text,
            "sourceLanguage": src_lang,
            "targetLanguage": dest_lang
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
