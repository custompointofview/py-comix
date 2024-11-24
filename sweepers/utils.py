
DEFAULT_PADDING_LENGTH = 4

def add_padding_number(nr):
    number = f"{nr}"
    for x in range(DEFAULT_PADDING_LENGTH - len(number)):
        number = "0" + number
    return number
