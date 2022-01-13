import datetime


def validDateFormat(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')

        return True
    except ValueError:
        return False
