"""
The Base62 stuff is a mix from Wikipedia and various stackoverflow, it allows
us to generate a keyword from a integer id.
"""

import re


ALPHABET="AaVjBGyp7bu4lvTUXxtqQSWD1gr6fO5K29NonPz3EHdIReFCMZswcmJY8kh0iL"
re_duration = re.compile(r"^(\d{,3})(h(our)?|d(ay)?|w(eek)?|m(onth)?|y(ear)?)s?$")


exp_multipliers = {
    "h": 60 * 60,
    "d": 60 * 60 * 24,
    "w": 60 * 60 * 24 * 7,
    "m": 60 * 60 * 24 * 30,
    "y": 60 * 60 * 24 * 365,
}


def extract_expiration(path):
    default = exp_multipliers["w"] * 2  # 2 weeks
    max_exp = exp_multipliers["y"] * 10 # 10 years

    if "+" not in path:
        return path, default

    path, exp = path.split("+", 1)
    m = re_duration.match(exp)

    if not m:
        return path, default

    return path, min(max_exp, (m.group(1)) * exp_multipliers[m.group(2)[0]])


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
