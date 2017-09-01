import random
import string
from random import randrange
from datetime import timedelta


def generate_string(length, lower_ch, upper_ch, digits):
    available_chars = ""

    if lower_ch:
        available_chars += string.ascii_lowercase

    if upper_ch:
        available_chars += string.ascii_uppercase

    if digits:
        available_chars += string.digits

    return ''.join(random.SystemRandom().choice(available_chars) for _ in range(length))


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)
