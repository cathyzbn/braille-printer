from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
from flask_cors import CORS

from utils.text_to_braille import text_to_braille

app = Flask(__name__)
CORS(app)  # Allow requests from your Next.js app

@app.route('/', methods=['POST'])
def handle_input():
    # If the request is multipart/form-data, treat it as a PDF upload.
    if request.content_type.startswith("multipart/form-data"):
        if 'file' in request.files:
            pdf_file = request.files['file']
            # Optionally, check for form field "type" if desired:
            # if request.form.get("type") != "pdf": return jsonify({"error": "Invalid type"}), 400

            pdf_reader = PdfReader(pdf_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() or ""
            braille_output = text_to_braille(extracted_text)
            print("Braille (PDF):", braille_output)
            return jsonify({"braille": braille_output}), 200
        return jsonify({"error": "No file provided"}), 400

    # If the request is JSON, treat it as a text submission.
    elif request.is_json:
        data = request.get_json()
        if data.get('type') == 'text':
            user_text = data.get('payload', "")
            braille_output = text_to_braille(user_text)
            print("Braille (Text):", braille_output)
            return jsonify({"braille": braille_output}), 200
        return jsonify({"error": "Invalid JSON payload"}), 400

    return jsonify({"error": "Unsupported Content-Type"}), 400


if __name__ == '__main__':
    app.run(port=6969, debug=True)
