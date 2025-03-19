from task_1 import add


def greetings():
    name = input("What is your name? ")

    return f"Hello, {name}!"

def add_from_input():
    number_1 = int(input("What is your first number? "))
    number_2 = int(input("What is your second number? "))

    return add(number_1, number_2)
