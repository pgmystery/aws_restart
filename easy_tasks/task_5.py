import random


def get_random_number():
    return random.randint(1, 100)

def guess_the_number_game():
    random_number = get_random_number()
    chances = 10

    while chances > 0:
        users_guess = int(input("Guess the number between 1 and 100: "))

        if users_guess == random_number:
            return "You got it!"
        else:
            if users_guess < random_number:
                print("Too low")
            elif users_guess > random_number:
                print("Too high")

            chances -= 1
            print(f"You got {chances} chances left")

    return f"Sorry, you didn't guess the number. The number was {str(random_number)}"

if __name__ == "__main__":
    print(get_random_number())
    print(guess_the_number_game())
