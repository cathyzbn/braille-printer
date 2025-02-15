def text_to_braille(text):
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
    
    result = ''
    for char in text.lower():
        result += braille_map.get(char, char)
    return result

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
