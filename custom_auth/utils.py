# utils.py
import random


def generate_4_digit_code():
    return str(random.randint(1000, 9999))
