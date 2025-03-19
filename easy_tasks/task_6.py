import datetime

def get_current_date_and_time():
    return str(datetime.datetime.now())

def get_days_till_birth():
    birthday_day = int(input("Enter birthday day: "))
    birthday_month = int(input("Enter birthday month: "))

    today = datetime.datetime.now()
    next_birthday = datetime.datetime(today.year, birthday_month , birthday_day)
    days_till_birth = next_birthday - today

    # Today is you birthday: hooray!!!
    if days_till_birth.days == -1:
        return 0

    # Check if you birthday already happened this year and take next year
    if days_till_birth.days < 0:
        next_birthday = datetime.datetime(today.year + 1, birthday_month , birthday_day)
        days_till_birth = next_birthday - today

    return days_till_birth.days + 1
