from process_text import text_to_braille
from braille_to_gcode import braille_str_to_gcode, CharPointer
from printer import print_gcode

if __name__ == "__main__":
    char_pointer = CharPointer()
    hello_braille = text_to_braille("abc!.,")
    print(hello_braille)
    actions = braille_str_to_gcode(hello_braille, char_pointer)
    print("\n".join(str(action) for action in actions))
    print_gcode(actions)