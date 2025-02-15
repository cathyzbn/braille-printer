def text_to_braille(text):
    """
    Converts text to braille representation using Unicode braille patterns.
    Each character is mapped to its corresponding braille pattern.
    
    Args:
        text (str): Input text to convert to braille
        
    Returns:
        str: Braille representation of the input text
    """
    braille_map = {
        'a': '⠁', 'b': '⠃', 'c': '⠉', 'd': '⠙', 'e': '⠑', 'f': '⠋',
        'g': '⠛', 'h': '⠓', 'i': '⠊', 'j': '⠚', 'k': '⠅', 'l': '⠇',
        'm': '⠍', 'n': '⠝', 'o': '⠕', 'p': '⠏', 'q': '⠟', 'r': '⠗',
        's': '⠎', 't': '⠞', 'u': '⠥', 'v': '⠧', 'w': '⠺', 'x': '⠭',
        'y': '⠽', 'z': '⠵', ' ': '⠀',
        '0': '⠴', '1': '⠂', '2': '⠆', '3': '⠒', '4': '⠲',
        '5': '⠢', '6': '⠖', '7': '⠶', '8': '⠦', '9': '⠔',
        '.': '⠨', ',': '⠠', '!': '⠮', '?': '⠹', 
    }
    
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


print(text_to_braille("Hi! My name is Cathy"))