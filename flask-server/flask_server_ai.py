from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import os
import base64
from pdf2image import convert_from_bytes
from io import BytesIO

load_dotenv()
client = anthropic.Anthropic()

app = Flask(__name__)
CORS(app)

def text_to_braille(text: str) -> str:
    braille_map = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋',
        'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
        'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗',
        's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
        'y': '⠽', 'z': '⠵', ' ': '⠀',
        '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲',
        '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
        '.': '⠨', ',': '⠠', '!': '⠮', '?': '⠹',
    }
    return "".join(braille_map.get(char, char) for char in text.lower())

@app.route('/', methods=['POST'])
def handle_input():
    if request.content_type.startswith("multipart/form-data"):
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
                transcription = response.content
                if isinstance(transcription, list):
                    transcription = "".join(str(item) for item in transcription)
                full_transcription += transcription + "\n\n"
            return jsonify({"text": full_transcription.strip()}), 200
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
