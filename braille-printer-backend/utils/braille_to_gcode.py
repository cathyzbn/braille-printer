from dataclasses import dataclass
from typing import List, Tuple
import fpdf

from utils.text_to_braille import text_to_braille

# Constants
MM_PER_UNIT = 2 # change for font
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

@dataclass
class DotPosition:
    """
    Position relative to page top
    """
    x: float
    y: float
    punch: bool
    page: int = 0

@dataclass 
class DotRelativeLocation:
    """
    Position relative to character top
    """
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

def get_dots_pos_and_page(braille_str: str) -> List[List[DotPosition]]:
    """Get dot positions for each page"""
    pages = [[]]
    x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
    y = TOP_MARGIN_HEIGHT * MM_PER_UNIT
    current_page = 0
    
    def new_line(x: float, y: float) -> Tuple[float, float]:
        x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
        y += (CHAR_HEIGHT + ROW_HEIGHT) * MM_PER_UNIT
        return x, y

    for char in braille_str:
        if char == '\n':
            x, y = new_line(x, y)
            continue
            
        char = BrailleChar(char)
        locations = char.get_dot_rel_loc()
        
        for loc in locations:
            abs_x = x + loc.x * MM_PER_UNIT
            abs_y = y + loc.y * MM_PER_UNIT
            pages[current_page].append(DotPosition(abs_x, abs_y, loc.punch, current_page))
            
        x += (CHAR_WIDTH + COLUMN_WIDTH) * MM_PER_UNIT
        if x + CHAR_WIDTH * MM_PER_UNIT > (PAPER_WIDTH - RIGHT_MARGIN_WIDTH) * MM_PER_UNIT:
            x, y = new_line(x, y)
            if y - CHAR_HEIGHT * MM_PER_UNIT > (PAPER_HEIGHT - BOTTOM_MARGIN_HEIGHT) * MM_PER_UNIT:
                current_page += 1
                pages.append([])
                x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
                y = TOP_MARGIN_HEIGHT * MM_PER_UNIT
                
    return pages

def dot_pos_to_pdf(dot_positions: List[DotPosition], output_file: str) -> None:
    """Convert dot positions to PDF"""
    pdf = fpdf.FPDF('P', 'mm', 'Letter')
    
    current_page = -1
    for dot in dot_positions:
        if dot.page > current_page:
            pdf.add_page()
            current_page = dot.page
            
        if dot.punch:
            pdf.ellipse(dot.x, dot.y,
                       DIST_DIAM_DOT * MM_PER_UNIT, 
                       DIST_DIAM_DOT * MM_PER_UNIT, 'F')
        else:
            pdf.ellipse(dot.x, dot.y,
                       DIST_DIAM_DOT * MM_PER_UNIT,
                       DIST_DIAM_DOT * MM_PER_UNIT, 'D')
    
    pdf.output(output_file)

    


def dot_pos_to_gcode(dot_positions: List[DotPosition]) -> List[GcodeAction]:
    """Convert dot positions to GCODE commands"""
    actions = []
    for dot in dot_positions:
        if dot.punch:
            actions.append(GcodeAction("G1 X{} Y{} F{}".format(
                PAPER_WIDTH * MM_PER_UNIT - dot.x,
                dot.y,
                SPEED_LATERAL
            )))
            actions.append(GcodeAction("G1 E{} F{}".format(PUNCH_AMOUNT, SPEED_PUNCH)))
    return actions


if __name__ == "__main__":
    hello_braille = text_to_braille("Wishing you a day filled with inspiration, creativity, and success!\nWhatever you're working on, know that your ideas have the power to make a difference. Keep pushing forward, stay curious, and never stop innovating.")
    dot_positions = get_dots_pos_and_page(hello_braille)
    
    # Generate PDF
    dot_pos_to_pdf([dot for page in dot_positions for dot in page], "hello.pdf")
    
    # Generate GCODE
    for page in dot_positions:
        for action in dot_pos_to_gcode(page):
            print(str(action))
