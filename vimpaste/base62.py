"""
This is coming from Wikipedia and various stackoverflow, it allows us to
generate a keyword from a integer id.
"""

ALPHABET="AaVjBGyp7bu4lvTUXxtqQSWD1gr6fO5K29NonPz3EHdIReFCMZswcmJY8kh0iL"

def b62encode(number):
    """
    Convert positive integer to a base62 string.
    """
    if not isinstance(number, (int, long)):
        raise TypeError('number must be an integer')
 
    # Special case for zero
    if number == 0:
        return '0'
 
    base62 = ''
 
    sign = ''
    if number < 0:
        sign = '-'
        number = - number
 
    while number != 0:
        number, i = divmod(number, len(ALPHABET))
        base62 = ALPHABET[i] + base62
 
    return sign + base62
 
def b62decode(string):
    """Decode a Base X encoded string into the number

    Arguments:
    - `string`: The encoded string
    """
    base = len(ALPHABET)
    strlen = len(string)
    num = 0

    idx = 0
    for char in string:
        power = (strlen - (idx + 1))
        num += ALPHABET.index(char) * (base ** power)
        idx += 1

    return num
