from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
from pdf_extraction import extract_text_from_pdf
import sys
sys.path.insert(0, "./utils")
from process_text import text_to_braille

load_dotenv()
client = anthropic.Anthropic()

app = Flask(__name__)
CORS(app)

"""
0. call: str_to_braille() -> braille
1. call func: get_dots_pos_and_page(braille) -> List[DotPositions]
    dot_pos[page][list of points]
2. call func: dot_pos_to_pdf(dot_pos[page]) -> pdf
3. call: print_dots(dot_pos[page]) -> backend prints
"""


@app.route('/', methods=['POST'])
def handle_input():
    if request.content_type.startswith("multipart/form-data"):
        if 'file' in request.files:
            pdf_file = request.files['file']
            pdf_bytes = pdf_file.read()
            transcript = extract_text_from_pdf(pdf_bytes)
            print(transcript)
            return jsonify({"text": transcript.strip()}), 200
        return jsonify({"error": "No file provided"}), 400

    elif request.is_json:
        data = request.get_json()
        if data.get('type') == 'text':
            user_text = data.get('payload', "")
            braille_output = text_to_braille(user_text)
            return jsonify({"braille": braille_output}), 200
        return jsonify({"error": "Invalid JSON payload"}), 400

    return jsonify({"error": "Unsupported Content-Type"}), 400

if __name__ == '__main__':
    app.run(port=6969, debug=True)
