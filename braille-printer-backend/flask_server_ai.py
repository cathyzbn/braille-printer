from io import BytesIO
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import atexit

from utils.pdf_extraction import extract_text_from_pdf
from utils.text_to_braille import text_to_braille
from utils.braille_to_gcode import DotPosition, dot_pos_to_pdf, get_dots_pos_and_page, dot_pos_to_gcode
from utils.printer import PrinterConnection, PrintStatus, pause_print, print_gcode, resume_print, stop_print

DEBUG = False

load_dotenv()
client = anthropic.Anthropic()

app = Flask(__name__)
CORS(app)

printer = None

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
    elif 'text' in request.form:
        transcript = request.form['text']
        braille = text_to_braille(transcript)
        dots_pos = get_dots_pos_and_page(braille)
        return jsonify(dots_pos), 200
    return jsonify({"error": "No file provided"}), 400

@app.route('/connect', methods=['POST'])
def handle_connect():
    global printer
    data = request.get_json()
    try:
        printer = PrinterConnection(data["port"], data["baudRate"])
        printer.connect()
    except Exception as e:
        printer.status = PrintStatus.ERROR
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": True}), 200

@app.route('/disconnect', methods=['POST'])
def handle_disconnect():
    global printer
    printer.close()
    printer = None
    return jsonify({"success": True}), 200

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
    print_gcode(actions, printer)
    return jsonify({"success": True}), 200

@app.route('/stop_print', methods=['POST'])
def handle_stop_print():
    stop_print(printer)
    return jsonify({"success": True}), 200

@app.route('/pause_print', methods=['POST'])
def handle_pause_print():
    pause_print(printer)
    return jsonify({"success": True}), 200

@app.route('/resume_print', methods=['POST'])
def handle_resume_print():
    resume_print(printer)
    return jsonify({"success": True}), 200


def cleanup():
    global printer
    if printer is not None:
        try:
            printer.close()
        except Exception as e:
            print(f"Error disconnecting printer: {e}")

atexit.register(cleanup)

if __name__ == '__main__':
    app.run(port=6969, debug=True)