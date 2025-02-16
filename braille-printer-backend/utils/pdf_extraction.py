
import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import anthropic
import base64
from groq import Groq
import time 

load_dotenv()
claude_client = anthropic.Anthropic()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

claude_model = "claude-3-haiku-20240307"
groq_model = "llama-3.2-11b-vision-preview"

groq_text_model = "llama3-8b-8192"


def extract_text_from_pdf(pdf_input, input_type="data"):
    if input_type == "path":
        pdf_doc = fitz.open(pdf_input)  # Open PDF
    elif input_type == "data":
        pdf_doc = fitz.open(stream=pdf_input, filetype="pdf")  # Open PDF from bytes
    else:
        raise ValueError("Invalid input type")
    elements = extract_elements_with_positions(pdf_doc)
    return format_elements(elements)

def format_elements(elements):
    """
    Formats the elements list by adding newlines between text elements and brackets around image descriptions.
    
    :param elements: List of tuples (type, content, position) from extract_elements_with_positions
    :return: Formatted string with the elements properly separated
    """
    formatted_text = ""
    for element_type, content, _ in elements:
        if element_type == "text":
            formatted_text += content + "\n"
        elif element_type == "image":
            formatted_text += f"[{content}]\n"
        else:
            raise ValueError(f"Invalid element type: {element_type}")

    # Use Groq to format and clean up the text
    groq_prompt = f"""Format and clean up this text to be more readable while preserving all information:

{formatted_text}

Make sure to:
1. Preserve all image descriptions in brackets
2. Keep proper paragraph spacing
3. Remove any redundant newlines
4. Ensure consistent formatting"""

    response = groq_client.chat.completions.create(
        model=groq_text_model,
        messages=[
            {"role": "user", "content": groq_prompt}
        ],
        temperature=0.1,
    )
    formatted_text = response.choices[0].message.content
    return formatted_text.strip()

def extract_elements_with_positions(pdf_doc, model=groq_model):
    """
    Extracts text and images from a PDF while preserving their order and positions.
    Uses both Claude and Groq models for image analysis.
    
    :param pdf_path: Path to the PDF file.
    :param output_folder: Folder to save extracted images.
    :return: List of elements in order with positions [(type, content, (x, y, width, height))].
    """ # Ensure output directory exists
    elements = []
    image_queries = []

    for page_num in range(len(pdf_doc)):
        page = pdf_doc[page_num]

        # Extract text with positions
        for text in page.get_text("blocks"):  # "blocks" returns text as (x0, y0, x1, y1, text, ...)
            x0, y0, x1, y1, content = text[:5]
            elements.append(("text", content.strip(), (x0, y0, x1 - x0, y1 - y0)))

        # Extract images with positions and prepare queries
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = pdf_doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_ext = base_image["ext"]
            bbox = page.get_image_rects(xref)[0]  # Get bounding box (x0, y0, x1, y1)
            x0, y0, x1, y1 = bbox

            # Convert image bytes to base64 for Claude
            image_b64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Store query info for both models
            image_queries.append({
                'claude_payload': [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": f"image/{img_ext}",
                            "data": image_b64,
                        },
                    },
                    {
                        "type": "text", 
                        "text": "Please describe this image in less than 3 sentences."
                    }
                ],
                'groq_payload': {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/{img_ext};base64,{image_b64}"
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": "Briefly describe this image in less than 3 sentences."
                                }
                            ]
                        }
                    ]
                },
                'position': (x0, y0, x1 - x0, y1 - y0)
            })

    # Send all image queries in parallel to both models
    if 'claude' in model:
        responses = claude_client.messages.create(
            model=model,
            max_tokens=1000,
            messages=[{"role": "user", "content": query['claude_payload']} for query in image_queries]
        )
        # Add image descriptions to elements list
        for response, query in zip(responses, image_queries):
            for response in response:
                elements.append(("image", response, query['position']))
    else:
        responses = [
            groq_client.chat.completions.create(
                model=groq_model,
                messages=query['groq_payload']["messages"],
                max_tokens=1000
            ) for query in image_queries
        ]
        # Add image descriptions to elements list
        for response, query in zip(responses, image_queries):
            elements.append(("image", response.choices[0].message.content, query['position']))
    return sorted(elements, key=lambda e: e[2][1])  # Sort by y-coordinate for top-down order


def test_model(model):
    start = time.time()
    print(format_elements(extract_elements_with_positions("test.pdf", model)))
    end = time.time()
    print(f"Time taken: {end - start} seconds")


def test_groq_image():
    # Read and encode the test image
    with open("test.png", "rb") as img_file:
        img_data = img_file.read()
        img_b64 = base64.b64encode(img_data).decode('utf-8')
    
    # Construct the payload
    payload = {
        "messages": [
            {
                "role": "user", 
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_b64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "Briefly describe this image in less than 3 sentences."
                    }
                ]
            }
        ]
    }

    # Send request to Groq
    response = groq_client.chat.completions.create(
        model=groq_model,
        messages=payload["messages"],
        max_tokens=1000
    )

    print("Groq Image Test Response:")
    print(response.choices[0].message.content)


# test_model(claude_model)
# test_model(groq_model)
# test_groq_image()
