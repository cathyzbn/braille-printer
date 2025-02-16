import fitz  # PyMuPDF
import os
from dotenv import load_dotenv
import anthropic
import base64
from groq import Groq
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
claude_client = anthropic.Anthropic()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

claude_model = "claude-3-haiku-20240307"
groq_model = "llama-3.2-11b-vision-preview"

groq_text_model = "llama3-8b-8192"
groq_fast_model = "llama-3.2-1b-preview"


def extract_text_from_pdf(pdf_input, input_type="data"):
    if input_type == "path":
        pdf_doc = fitz.open(pdf_input)  # Open PDF
    elif input_type == "data":
        pdf_doc = fitz.open(stream=pdf_input, filetype="pdf")  # Open PDF from bytes
    else:
        raise ValueError("Invalid input type")
    elements = extract_elements_with_positions(pdf_doc)
    return format_elements(elements)


def get_full_transcript(zoom_url):
    # Set up headless Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    try:
        # Load the Zoom transcript page
        driver.get(zoom_url)
        print(zoom_url)
        # Wait for transcript list to load
        transcript_list = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "transcript-list"))
        )
        
        # Execute JavaScript to extract messages
        transcript = driver.execute_script("""
            const transcriptList = document.querySelector('.transcript-list');
            const transcriptListItems = transcriptList.querySelectorAll('li');
            
            const messages = [];
            transcriptListItems.forEach(item => {
                const userName = item.querySelector('.user-name');
                if (userName) {
                    const user = userName.textContent;
                    const text = item.querySelector('.text').textContent;
                    messages.push({
                        user: user,
                        text: text
                    });
                } else {
                    messages[messages.length - 1].text += '\\n' + item.querySelector('.text').textContent;
                }
            });
            
            return messages;
        """)
        
        # Format transcript into string
        full_transcript = ""
        for message in transcript:
            full_transcript += f"{message['user']}: {message['text']}\n"
            
        return full_transcript
        
    finally:
        driver.quit()


def extract_text_from_zoom(zoom_url):
    # f = open("braille-printer-backend/transcript.vtt", "r")
    # raw_transcript = f.read()
    raw_transcript = get_full_transcript(zoom_url)
    print("raw_transcript", len(raw_transcript))
    transcript = ""
    for line in raw_transcript.split("\n"):
        if ":" in line and not line[0].isdigit():
            # Get everything after the colon and strip whitespace
            transcript += line.split(":", 1)[1].strip() + " "

    # Split transcript into chunks of roughly 2000 tokens each
    # (A rough estimate is ~4 chars per token)
    chunk_size = 8000  # characters
    chunks = [transcript[i:i+chunk_size] for i in range(0, len(transcript), chunk_size)]

    summaries = []
    # Create prompts for all chunks
    prompts = []
    for chunk in chunks:
        groq_prompt = f"""Summarize this portion of a lecture transcript concisely, focusing on key points:

{chunk}

Focus on:
1. Main topics and concepts
2. Key technical details
3. Clear and readable format"""
        prompts.append({
            "messages": [{"role": "user", "content": groq_prompt}],
            "temperature": 0.3
        })

    # Submit all chunks in parallel
    responses = [
        groq_client.chat.completions.create(
            model=groq_fast_model,
            **prompt
        ) for prompt in prompts
    ]
    print("responses", len(responses))

    # Extract summaries from responses
    for response in responses:
        summaries.append(response.choices[0].message.content.strip())\

    # Combine the summaries
    combined_summary = "\n\n".join(summaries)

    # Final pass to create cohesive summary
    final_prompt = f"""Create a cohesive summary from these section summaries:

{combined_summary}

Make it clear and well-structured."""
    print("final prompt", len(final_prompt))
    final_response = groq_client.chat.completions.create(
        model=groq_text_model,
        messages=[
            {"role": "user", "content": final_prompt}
        ],
        temperature=0.3,
    )

    return final_response.choices[0].message.content.strip()


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
    """  # Ensure output directory exists
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

print(extract_text_from_zoom("https://us04web.zoom.us/rec/play/oXI-CSzD0NWzsxNATlCxBYPEZouXI9kWJ1jjMMHWN49yVAdvhZ9jUtECtVnaRy6qOTSKEH7RkN32gRx8.3tz9oNZiRYWODs8A?accessLevel=meeting&canPlayFromShare=true&from=share_recording_detail&continueMode=true&componentName=rec-play&originRequestUrl=https%3A%2F%2Fus04web.zoom.us%2Frec%2Fshare%2FIFMNlVsAA2LQaRPLZDnRzoBsx48kqko3pcfZRmY3g31Vur5a4Iwy4oOdPWsHih6w.mKp3UDiKLnOClM7y%3FfromShareWithMe%3Dtrue")
)