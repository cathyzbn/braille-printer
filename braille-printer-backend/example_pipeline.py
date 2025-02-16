from utils.text_to_braille import text_to_braille
from utils.braille_to_gcode import get_dots_pos_and_page, dot_pos_to_gcode
from utils.printer import print_gcode

import sys
sys.path.append('utils')


if __name__ == "__main__":
    # Convert text to braille
    hello_braille = text_to_braille("Hello my name is Cathy")
    print("Braille string:", hello_braille)
    
    # Get dot positions for each page
    dot_positions = get_dots_pos_and_page(hello_braille)
    
    # # Generate PDF preview
    # dot_pos_to_pdf([dot for page in dot_positions for dot in page], "example.pdf")
    # print("Generated PDF preview as example.pdf")
    
    # Generate and print GCODE
    for page_num, page in enumerate(dot_positions):
        print(f"\nGenerating GCODE for page {page_num + 1}:")
        actions = dot_pos_to_gcode(page)
        print_gcode(actions)
        for action in actions:
            print(str(action))
