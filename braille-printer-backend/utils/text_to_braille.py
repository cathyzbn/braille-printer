# import pybrl as brl

def text_to_braille_grade1(text) -> str:
    """
    Converts text to braille representation using Unicode braille patterns.
    Each character is mapped to its corresponding braille pattern.
    
    Args:
        text (str): Input text to convert to braille
        
    Returns:
        str: Braille representation of the input text
    """
    # TODO(cathy): format tabs?
    chars = " A1B'K2L@CIF/MSP\"E3H9O6R^DJG>NTQ,*5<-U8V.%[$+X!&;:4\\0Z7(_?W]#Y)="
    brailles = "⠀⠁⠂⠃⠄⠅⠆⠇⠈⠉⠊⠋⠌⠍⠎⠏⠐⠑⠒⠓⠔⠕⠖⠗⠘⠙⠚⠛⠜⠝⠞⠟⠠⠡⠢⠣⠤⠥⠦⠧⠨⠩⠪⠫⠬⠭⠮⠯⠰⠱⠲⠳⠴⠵⠶⠷⠸⠹⠺⠻⠼⠽⠾⠿"
    braille_map = dict(zip(chars, brailles))
    braille_map['\n'] = '\n'
    
    return ''.join(braille_map.get(char, char) for char in text.upper())


# def text_to_braille_grade2(text) -> str:
#     """
#     Converts text to braille representation using Unicode braille patterns.
#     Each character is mapped to its corresponding braille pattern.
    
#     Args:
#         text (str): Input text to convert to braille
        
#     Returns:
#         str: Braille representation of the input text
#     """
#     return brl.toUnicodeSymbols(brl.translate(text), flatten=True)


def text_to_braille(text, grade=2) -> str:
    if grade == 1:
        return text_to_braille_grade1(text)
    elif grade == 2:
        print("WARNING: Grade 2 braille conversion is currently disabled")
        return text_to_braille_grade1(text)
    else:
        raise ValueError(f"Invalid grade for braille conversion: {grade}")


def test_braille_conversion():
    """Test function to verify braille conversion"""
    test_cases = [
        ("hello world", "⠓⠑⠇⠇⠕⠀⠺⠕⠗⠇⠙"),
        ("12345", "⠂⠆⠒⠲⠢"),
        ("Braille!", "⠃⠗⠁⠊⠇⠇⠑⠮")
    ]
    
    for input_text, expected in test_cases:
        result = text_to_braille(input_text)
        assert result == expected, f"Failed: {input_text} -> Got {result}, Expected {expected}"
