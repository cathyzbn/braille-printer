from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import base64
from pdf2image import convert_from_bytes
from io import BytesIO

from utils.pdf_extraction import extract_text_from_pdf
from utils.process_text import text_to_braille
from utils.braille_to_gcode import dot_pos_to_pdf, get_dots_pos_and_page, dot_pos_to_gcode
from utils.printer import print_gcode

load_dotenv()
client = anthropic.Anthropic()

app = Flask(__name__)
CORS(app)

DEBUG = False

# pdf to dot positions
# right now it's pdf to ascii
@app.route('/', methods=['POST'])
def handle_input():
    if 'file' in request.files:
        pdf_file = request.files['file']
        pdf_bytes = pdf_file.read()
        transcript = extract_text_from_pdf(pdf_bytes)
        if DEBUG:
            print("DEBUG: transcript", transcript)
        braille = text_to_braille(transcript)
        dots_pos = get_dots_pos_and_page(braille)
        return jsonify(dots_pos), 200
    return jsonify({"error": "No file provided"}), 400

@app.route('/dot_pos_to_pdf', methods=['POST'])
def handle_dot_pos_to_pdf(dot_positions):
    dot_pos_to_pdf(dot_positions, "braille.pdf")
    return send_file("braille.pdf", mimetype='application/pdf')

@app.route('/print_dots', methods=['POST'])
def handle_print_dots(dot_positions):
    actions = dot_pos_to_gcode(dot_positions)
    print_gcode(actions)
    return jsonify({"success—printing...": True}), 200

if __name__ == '__main__':
    app.run(port=6969, debug=True)