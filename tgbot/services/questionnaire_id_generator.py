import random, string


def get_rand_id(length):
    letters = string.ascii_lowercase + string.ascii_uppercase
    digits = string.digits
    symbols = letters + digits
    return ''.join(random.choice(symbols) for i in range(length))
