import random

def generate_new_cart_id():
    # Generate a random 10-digit number
    return str(random.randint(1000000000, 9999999999))
