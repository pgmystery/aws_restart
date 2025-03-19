def is_even(num) -> bool:
    return num % 2 == 0

def human_category(age: int) -> str:
    match age:
        case _ if 0 > age:
            return "You are not even born!"
        case _ if 0 <= age <= 12:
            return "You are a child!"
        case _ if 13 <= age <= 19:
            return "You are a Teenager!"
        case _ if 20 <= age <= 64:
            return "You are a Adult!"
        case _ if age > 64:
            return "You are a Senior!"
