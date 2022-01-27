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

        # only write that cc if you can get this value or above in premium (per contract)
        'minYield': 3.00,

        # prevent paying for rollups (can ignore minGapToATM, minStrike and minYield!)
        'rollWithoutDebit': True,

        # if we can't get filled on an order, how much is the bot allowed to
        # reduce the price from mid price to try and get a fill (percentage 0-100)
        'allowedPriceReductionPercent': 2
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
