from dataclasses import dataclass
from typing import List
import fpdf

from process_text import text_to_braille

# Constants
MM_PER_UNIT = 2
# Diameter of one dot is 1 unit
DIST_DIAM_DOT = 1
DIST_BETWEEN_DOTS = 1

CHAR_HEIGHT = 3 * DIST_DIAM_DOT + 2 * DIST_BETWEEN_DOTS
CHAR_WIDTH = 2 * DIST_DIAM_DOT + DIST_BETWEEN_DOTS
PUNCH_AMOUNT = 2

COLUMN_WIDTH = 2
ROW_HEIGHT = 2

PAPER_WIDTH = 210 / MM_PER_UNIT
PAPER_HEIGHT = 297 / MM_PER_UNIT

LEFT_MARGIN_WIDTH = 10
RIGHT_MARGIN_WIDTH = 10
TOP_MARGIN_HEIGHT = 20
BOTTOM_MARGIN_HEIGHT = 20

SPEED_LATERAL = 4000 # 4000
SPEED_PUNCH = 800

DEBUG = False

# TODO(cathy) spacing options
# TODO(cathy / jason) support for math?

@dataclass
class DotRelativeLocation:
    x: int
    y: int
    punch: bool

class BrailleChar:
    def __init__(self, braille_ascii) -> None:
        dots = ord(braille_ascii) - 0x2800

        # Dot pattern in binary:
        # 1 4
        # 2 5 
        # 3 6
        self.first = True if dots & 0x1 else False
        self.second = True if dots & 0x2 else False
        self.third = True if dots & 0x4 else False
        self.fourth = True if dots & 0x8 else False
        self.fifth = True if dots & 0x10 else False
        self.sixth = True if dots & 0x20 else False
    
    def get_dot_rel_loc(self) -> list[DotRelativeLocation]:
        locations = []
        locations.append(DotRelativeLocation(0, 0, self.first))
        locations.append(DotRelativeLocation(0, DIST_DIAM_DOT+DIST_BETWEEN_DOTS, self.second))
        locations.append(DotRelativeLocation(0, DIST_DIAM_DOT*2+DIST_BETWEEN_DOTS*2, self.third))
        locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, 0, self.fourth))
        locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, DIST_DIAM_DOT+DIST_BETWEEN_DOTS, self.fifth))
        locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, DIST_DIAM_DOT*2+DIST_BETWEEN_DOTS*2, self.sixth))
        return locations


class GcodeAction:
    def __init__(self, command: str) -> None:
        self.command = command

    def __str__(self) -> str:
        return self.command


class CharPointer:
    def __init__(self) -> None:
        self.x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
        self.y = TOP_MARGIN_HEIGHT * MM_PER_UNIT
    
    def next_char(self) -> None:
        self.x += (CHAR_WIDTH + COLUMN_WIDTH) * MM_PER_UNIT
        if self.x + CHAR_WIDTH * MM_PER_UNIT > PAPER_WIDTH * MM_PER_UNIT - RIGHT_MARGIN_WIDTH * MM_PER_UNIT:
            self.x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
            self.y += (CHAR_HEIGHT + ROW_HEIGHT) * MM_PER_UNIT
        if self.y > PAPER_HEIGHT * MM_PER_UNIT - BOTTOM_MARGIN_HEIGHT * MM_PER_UNIT:
            raise Exception("Out of paper")


def braille_str_to_gcode(braille_str, char_pointer: CharPointer) -> List[GcodeAction]:
    actions = []
    for char in braille_str:
        if char == '\n':
            char_pointer.next_char()
            continue
        char = BrailleChar(char)
        locations = char.get_dot_rel_loc()
        for location in locations:
            if location.punch:
                actions.append(GcodeAction("G1 X{} Y{} F{}".format(
                    # Flip on print!
                    PAPER_WIDTH * MM_PER_UNIT - (char_pointer.x + location.x * MM_PER_UNIT), 
                    char_pointer.y + location.y * MM_PER_UNIT, 
                    SPEED_LATERAL
                )))
                actions.append(GcodeAction("G1 E{} F{}".format(PUNCH_AMOUNT, SPEED_PUNCH)))
        if DEBUG:
            actions.append(GcodeAction("Next Char"))
        char_pointer.next_char()
    return actions

def braille_to_pdf(braille_str: str, output_file: str) -> None:
    """
    Convert text to braille and create a PDF visualization
    Args:
        text: Input text to convert to braille
        output_file: Path to save the PDF file
    """
    
    # Create PDF
    pdf = fpdf.FPDF('P', 'mm', 'Letter')
    pdf.add_page()
    
    # Set initial position
    x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
    y = TOP_MARGIN_HEIGHT * MM_PER_UNIT

    def new_line(x, y):
        x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
        y += (CHAR_HEIGHT + ROW_HEIGHT) * MM_PER_UNIT
        return x, y
    
    # Draw each braille character
    for char in braille_str:
        if char == '\n':
            x, y = new_line(x, y)
            continue
        char = BrailleChar(char)
        locations = char.get_dot_rel_loc()
        for loc in locations:
            # Convert relative locations to absolute positions
            abs_x = x + loc.x * MM_PER_UNIT
            abs_y = y + loc.y * MM_PER_UNIT
            # Draw dot as small circle
            if loc.punch:
                pdf.ellipse(abs_x, abs_y, 
                          DIST_DIAM_DOT * MM_PER_UNIT, DIST_DIAM_DOT * MM_PER_UNIT, 'F')
            else:
                pdf.ellipse(abs_x, abs_y,
                          DIST_DIAM_DOT * MM_PER_UNIT, DIST_DIAM_DOT * MM_PER_UNIT, 'D')
        # Move to next character position
        x += (CHAR_WIDTH + COLUMN_WIDTH) * MM_PER_UNIT
        if x + CHAR_WIDTH * MM_PER_UNIT > (PAPER_WIDTH - RIGHT_MARGIN_WIDTH) * MM_PER_UNIT:
            x, y = new_line(x, y)
            if y - CHAR_HEIGHT * MM_PER_UNIT > (PAPER_HEIGHT - BOTTOM_MARGIN_HEIGHT) * MM_PER_UNIT:
                pdf.add_page()
                x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
                y = TOP_MARGIN_HEIGHT * MM_PER_UNIT
    
    # Save PDF
    pdf.output(output_file)


if __name__ == "__main__":
    char_pointer = CharPointer()
    hello_braille = text_to_braille("Wishing you a day filled with inspiration, creativity, and success!\nWhatever you’re working on, know that your ideas have the power to make a difference. Keep pushing forward, stay curious, and never stop innovating.")
    # braille_to_pdf(hello_braille, "hello.pdf")
    for x in braille_str_to_gcode(hello_braille, char_pointer):
        print(str(x))
