from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import base64
from pdf2image import convert_from_bytes
from io import BytesIO

from utils.process_text import text_to_braille
from utils.braille_to_gcode import dot_pos_to_pdf, get_dots_pos_and_page, dot_pos_to_gcode
from utils.printer import print_gcode

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
        images = convert_from_bytes(pdf_bytes)
        full_transcription = ""
        for page in images:
            buffered = BytesIO()
            page.save(buffered, format="PNG")
            image_data = base64.standard_b64encode(buffered.getvalue()).decode("utf-8")
            message_payload = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "transcribe this image to a pdf verbatim. include [image descriptions]. don't write code for this. Don't include any other commentary, just the text transcription, starting now:"
                }
            ]
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2048,
                messages=[{"role": "user", "content": message_payload}]
            )
            transcription = response.content[0].text
            # remove unnec spaces (i.e. "hi  jeff" -> "hi jeff")
            # transcription = " ".join(transcription.split())
            if isinstance(transcription, list):
                transcription = "".join(str(item) for item in transcription)
            full_transcription += transcription + "\n\n"
        braille = text_to_braille(full_transcription)
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
