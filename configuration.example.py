apiKey = ''  # create an app on https://developer.tdameritrade.com/ to get one
apiRedirectUri = 'https://localhost'
ameritradeAccountId = ''

dbName = 'db.json'

# console, email ### where to alert regarding errors or order fills
botAlert = 'console'

configuration = {
    'QQQ': {
        # how many cc's to write
        'amountOfHundreds': 1,

        # only write cc's at or over current asset price + this value
        'minGapToATM': 1,

        # don't write cc's with strikes below this value
        'minStrike': 0,

        # write cc's around this far out, bot gets the nearest contract possible
        'days': 30,

        # allow x days less or more
        'daysSpread': 10,

        # only write that cc if you can get this value or above in premium
        'minYield': 3.00,

        # prevent paying for rollups (CAN IGNORE minGapToATM, minStrike and minYield!!!)
        'rollWithoutDebit': True
    }
}

# Required for 'botAlert' email
mailConfig = {
    'smtp': None,
    'port': 587,
    'from': None,
    'to': None,
    'username': None,
    'password': None,
}

# don't touch these
debugMarketOpen = False
debugEverythingNeedsRolling = False
debugCanSendOrders = True
