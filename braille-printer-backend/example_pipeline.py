from utils.braille_to_gcode import get_dots_pos_and_page, dot_pos_to_gcode, dot_pos_to_pdf
from utils.pdf_extraction import extract_text_from_pdf
from utils.printer import print_gcode

import sys
sys.path.append('utils')


if __name__ == "__main__":
    # Convert text to braille
    # text = text_to_braille("Hello my name is Cathy")
    # print("Braille string:", text)

    text = extract_text_from_pdf("test.pdf", input_type="path")
    
    # Get dot positions for each page
    dot_positions = get_dots_pos_and_page(text)
    
    # Generate PDF preview
    pdf = dot_pos_to_pdf([dot for page in dot_positions for dot in page])
    pdf.output("test_output.pdf")
    print("Generated PDF preview as test_output.pdf")
    
    # Generate and print GCODE
    for page_num, page in enumerate(dot_positions):
        print(f"\nGenerating GCODE for page {page_num + 1}:")
        actions = dot_pos_to_gcode(page)
        print_gcode(actions)
        for action in actions:
            print(str(action))
