from dataclasses import dataclass
from typing import List, Tuple
import fpdf

from utils.text_to_braille import text_to_braille

# Constants
MM_PER_UNIT = 1.5 # change for font
# Diameter of one dot is 1 unit
DIST_DIAM_DOT = 1
DIST_BETWEEN_DOTS = 1

CHAR_HEIGHT = 3 * DIST_DIAM_DOT + 2 * DIST_BETWEEN_DOTS
CHAR_WIDTH = 2 * DIST_DIAM_DOT + DIST_BETWEEN_DOTS
PUNCH_AMOUNT = 2

COLUMN_WIDTH = 3
ROW_HEIGHT = 4

PAPER_WIDTH = 215.9 / MM_PER_UNIT
PAPER_HEIGHT = 279.4 / MM_PER_UNIT

LEFT_MARGIN_WIDTH = 25 / MM_PER_UNIT
RIGHT_MARGIN_WIDTH = 25 / MM_PER_UNIT
TOP_MARGIN_HEIGHT = 25 / MM_PER_UNIT
BOTTOM_MARGIN_HEIGHT = 25 / MM_PER_UNIT

# Offset of the page's origin relative to the printer's origin
LEFT_OFFSET = 23
TOP_OFFSET = 30

SPEED_LATERAL = 4000 # 4000
SPEED_PUNCH = 800

NUM_BRAILLE_PER_ROW = int((PAPER_WIDTH - LEFT_MARGIN_WIDTH - RIGHT_MARGIN_WIDTH - CHAR_WIDTH) / (CHAR_WIDTH + COLUMN_WIDTH)) + 1
NUM_BRAILLE_PER_COL = int((PAPER_HEIGHT - TOP_MARGIN_HEIGHT - BOTTOM_MARGIN_HEIGHT - CHAR_HEIGHT) / (CHAR_HEIGHT + ROW_HEIGHT)) + 1
ACTUAL_COL_WIDTH = (PAPER_WIDTH - LEFT_MARGIN_WIDTH - RIGHT_MARGIN_WIDTH - CHAR_WIDTH * NUM_BRAILLE_PER_ROW) / (NUM_BRAILLE_PER_ROW -1)
ACTUAL_ROW_HEIGHT = (PAPER_HEIGHT - TOP_MARGIN_HEIGHT - BOTTOM_MARGIN_HEIGHT - CHAR_HEIGHT * NUM_BRAILLE_PER_COL) / (NUM_BRAILLE_PER_COL -1)

DEBUG = False

class PrintedDots:
    def __init__(self):
        self.dots = []

    def clear(self):
        self.dots = []

    def append(self, dot):
        self.dots.append(dot)

printed_dots = PrintedDots()

@dataclass
class DotPosition:
    """
    Position relative to page top
    """
    x: float
    y: float
    punch: bool
    page: int = 0

    def copy(self):
        return DotPosition(self.x, self.y, self.punch, self.page)

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
    def __init__(self, command: str, dot: DotPosition = None) -> None:
        self.command = command
        self.dot = dot.copy() if dot else None

    def callback(self):
        if self.dot:
            printed_dots.append(self.dot)

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
        y += (CHAR_HEIGHT + ACTUAL_ROW_HEIGHT) * MM_PER_UNIT
        return x, y

    for char in braille_str:
        if char == '\n':
            x, y = new_line(x, y)
            continue
            
        char = BrailleChar(char)
        locations = char.get_dot_rel_loc()

        if x + CHAR_WIDTH * MM_PER_UNIT - DIST_DIAM_DOT > (PAPER_WIDTH - RIGHT_MARGIN_WIDTH) * MM_PER_UNIT:
            x, y = new_line(x, y)
        if y + CHAR_HEIGHT * MM_PER_UNIT - DIST_DIAM_DOT > (PAPER_HEIGHT - BOTTOM_MARGIN_HEIGHT) * MM_PER_UNIT:
            current_page += 1
            pages.append([])
            x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
            y = TOP_MARGIN_HEIGHT * MM_PER_UNIT
        
        for loc in locations:
            abs_x = x + loc.x * MM_PER_UNIT
            abs_y = y + loc.y * MM_PER_UNIT
            pages[current_page].append(DotPosition(abs_x, abs_y, loc.punch, current_page))
            
        x += (CHAR_WIDTH + ACTUAL_COL_WIDTH) * MM_PER_UNIT
                      
    return pages

def dot_pos_to_pdf(dot_positions: List[DotPosition]) -> fpdf.FPDF:
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
    return pdf


def dot_pos_to_gcode(dot_positions: List[DotPosition]) -> List[GcodeAction]:
    """Convert dot positions to GCODE commands"""
    actions = []
    printed_dots.clear()
    for dot in dot_positions:
        if dot.punch:
            actions.append(GcodeAction("G1 X{} Y{} F{}".format(
                dot.x + LEFT_OFFSET,
                dot.y + TOP_OFFSET,
                SPEED_LATERAL
            )))
            actions.append(GcodeAction("G1 E{} F{}".format(PUNCH_AMOUNT, SPEED_PUNCH), dot))
    return actions


if __name__ == "__main__":
    hello_braille = text_to_braille("Wishing you a day filled with inspiration, creativity, and success!\nWhatever you're working on, know that your ideas have the power to make a difference. Keep pushing forward, stay curious, and never stop innovating.")
    dot_positions = get_dots_pos_and_page(hello_braille)
    
    # Generate PDF
    pdf = dot_pos_to_pdf([dot for page in dot_positions for dot in page])
    pdf.output("test_output.pdf")
    
    # Generate GCODE
    for page in dot_positions:
        for action in dot_pos_to_gcode(page):
            print(str(action))
