from flask import Flask, render_template, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# List of languages supported by GoogleTranslator
SUPPORTED_LANGUAGES = GoogleTranslator.get_supported_languages(as_dict=True)

@app.route("/", methods=["GET", "POST"])
def index():
    translated_text = ""
    if request.method == "POST":
        text = request.form["text"]
        src_lang = request.form["src_lang"]
        dest_lang = request.form["dest_lang"]

        try:
            translated_text = GoogleTranslator(source=src_lang, target=dest_lang).translate(text)
        except Exception as e:
            translated_text = f"Error: {str(e)}"

    return render_template(
        "index.html",
        translated_text=translated_text,
        languages=SUPPORTED_LANGUAGES
    )

if __name__ == "__main__":
    app.run(debug=True)
