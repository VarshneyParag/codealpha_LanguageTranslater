from flask import Flask, render_template, request, jsonify
from deep_translator import GoogleTranslator, exceptions
from datetime import datetime
import logging

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        max_chars=5000,
        now=datetime.now()  # Add this line to pass current datetime
    )

if __name__ == "__main__":
    app.run(debug=True)
