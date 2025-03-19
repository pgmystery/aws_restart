import math


def get_square_root(num: int) -> float:
    # return num ** 0.5
    return math.sqrt(num)

def get_round_numbers(num: float) -> tuple[int, int]:
    return math.floor(num), math.ceil(num)
