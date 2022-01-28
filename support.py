import datetime
from dateutil.relativedelta import relativedelta


def validDateFormat(date):
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')

        return True
    except ValueError:
        return False


def getNewCcExpirationDate():
    now = datetime.datetime.utcnow()
    now = now.replace(tzinfo=datetime.timezone.utc)

    third = getThirdFridayOfMonth(now)

    # if we are within 7 days or past, get the same day next month
    if now.day > third.day - 7:
        nextMonth = now + relativedelta(months=1)

        third = getThirdFridayOfMonth(nextMonth)

    return third


def getThirdFridayOfMonth(monthDate):
    # the third friday will be the 15 - 21 day, check lowest
    third = datetime.date(monthDate.year, monthDate.month, 15)

    w = third.weekday()
    if w != 4:
        # replace the day
        third = third.replace(day=(15 + (4 - w) % 7))

    return third


def getDeltaDiffNowTomorrow1Am():
    now = datetime.datetime.utcnow()

    tomorrow = datetime.datetime.combine(now.date(), datetime.time(0, 0)) + datetime.timedelta(days=1,hours=1)

    delta = tomorrow - now

    return delta
