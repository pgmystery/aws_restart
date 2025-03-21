def count_to_ten():
    for number in range(1, 11):
        print(number)

def count_to_ten_even():
    for number in range(1, 11):
        if number % 2 == 0:
            print(number)

def print_multiplication_table(number, up_to=10):
    for i in range(1, up_to + 1):
        result = number * i

        print(f"{number} x {i} = {result}")
