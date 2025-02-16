from io import BytesIO
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic

from utils.pdf_extraction import extract_text_from_pdf
from utils.text_to_braille import text_to_braille
from utils.braille_to_gcode import DotPosition, dot_pos_to_pdf, get_dots_pos_and_page, dot_pos_to_gcode
from utils.printer import print_gcode

DEBUG = False

load_dotenv()
client = anthropic.Anthropic()

app = Flask(__name__)
CORS(app)

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
def handle_dot_pos_to_pdf():
    data = request.get_json()
    # data["dotPositions"] can be either a list of DotPositions or list of list-of-DotPositions
    # If you only sent the single page, it's a list of DotPositions
    dot_positions = data["dotPositions"]
    dot_positions = [DotPosition(**dot_dict) for dot_dict in dot_positions]

    # If your 'dot_positions' is a nested list, you might need to flatten it:
    # flatten_dot_positions = [dot for page in dot_positions for dot in page]
    #
    # If it’s already a single list, skip flattening.

    pdf = dot_pos_to_pdf(dot_positions)
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return send_file(
        BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name="braille.pdf"
    )

@app.route('/print_dots', methods=['POST'])
def handle_print_dots():
    data = request.get_json()

    dot_positions = data["dotPositions"]
    dot_positions = [DotPosition(**dot_dict) for dot_dict in dot_positions]

    # convert from 
    actions = dot_pos_to_gcode(dot_positions)
    print_gcode(actions)
    return jsonify({"success—printing...": True}), 200

if __name__ == '__main__':
    app.run(port=6969, debug=True)