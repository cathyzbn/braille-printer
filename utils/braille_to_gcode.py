from dataclasses import dataclass
from typing import List

from utils.process_text import text_to_braille

# Constants
MM_PER_UNIT = 0.05
# Diameter of one dot is 1 unit
DIST_DIAM_DOT = 1
DIST_BETWEEN_DOTS = 1

CHAR_HEIGHT = 3 * DIST_DIAM_DOT + 2 * DIST_BETWEEN_DOTS
CHAR_WIDTH = 2 * DIST_DIAM_DOT + DIST_BETWEEN_DOTS
CHAR_DEPTH = 1

COLUMN_WIDTH = 2
ROW_HEIGHT = 2

PAPER_WIDTH = 210
PAPER_HEIGHT = 297

LEFT_MARGIN_WIDTH = 10
RIGHT_MARGIN_WIDTH = 10
TOP_MARGIN_HEIGHT = 20
BOTTOM_MARGIN_HEIGHT = 20

DEBUG = True

# TODO(cathy) spacing options
# TODO(cathy / jason) support for math?

@dataclass
class DotRelativeLocation:
    x: int
    y: int

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

        if self.first:
            locations.append(DotRelativeLocation(0, 0))
        if self.second:
            locations.append(DotRelativeLocation(0, DIST_DIAM_DOT+DIST_BETWEEN_DOTS))
        if self.third:
            locations.append(DotRelativeLocation(0, DIST_DIAM_DOT*2+DIST_BETWEEN_DOTS*2))
        if self.fourth:
            locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, 0))
        if self.fifth:
            locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, DIST_DIAM_DOT+DIST_BETWEEN_DOTS))
        if self.sixth:
            locations.append(DotRelativeLocation(DIST_DIAM_DOT+DIST_BETWEEN_DOTS, DIST_DIAM_DOT*2+DIST_BETWEEN_DOTS*2))
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
        self.z = 0
    
    def next_char(self) -> None:
        self.x += (CHAR_WIDTH + COLUMN_WIDTH) * MM_PER_UNIT
        if self.x > PAPER_WIDTH - RIGHT_MARGIN_WIDTH * MM_PER_UNIT:
            self.x = LEFT_MARGIN_WIDTH * MM_PER_UNIT
            self.y += (CHAR_HEIGHT + ROW_HEIGHT) * MM_PER_UNIT
        if self.y > PAPER_HEIGHT - BOTTOM_MARGIN_HEIGHT * MM_PER_UNIT:
            raise Exception("Out of paper")


def braille_str_to_gcode(braille_str, char_pointer: CharPointer) -> List[GcodeAction]:
    braille_chars = [BrailleChar(char) for char in braille_str]
    actions = []
    for char in braille_chars:
        # actions.append(GcodeAction("G1 X{} Y{} Z{}".format(char_pointer.x, char_pointer.y, char_pointer.z)))
        locations = char.get_dot_rel_loc()
        for location in locations:
            actions.append(GcodeAction("G1 X{} Y{} Z{}".format(char_pointer.x + location.x * MM_PER_UNIT, char_pointer.y + location.y * MM_PER_UNIT, char_pointer.z)))
            actions.append(GcodeAction("G1 Z{}".format(char_pointer.z - CHAR_DEPTH * MM_PER_UNIT)))
            actions.append(GcodeAction("G1 Z{}".format(char_pointer.z)))
        if DEBUG:
            actions.append(GcodeAction("Next Char"))
        char_pointer.next_char()
    return actions


if __name__ == "__main__":
    char_pointer = CharPointer()
    hello_braille = text_to_braille("abc!.,")
    print(hello_braille)
    print("\n".join(str(action) for action in braille_str_to_gcode(hello_braille, char_pointer)))
