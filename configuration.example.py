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

        # write cc's at or over current asset price + this value
        'minGapToATM': 1,

        # If our strike is below current asset price - this value, we consider it deep ITM and want to rollup for debit
        'deepITMLimit': 10,

        # How much do we want to rollup the strike from last month if we are Deep ITM?
        # (Set this to 0 if you don't ever wanna pay for rollup)
        'deepITMMaxRollupGap': 0,

        # How much are we allowed to reduce the strike from last month? (flash crash protection)
        # If the underlying f.ex. drops by 30 in value, this is the max we are gonna drop our cc strike
        'maxDrawdownGap': 10,

        # don't write cc's with strikes below this value (set this f.ex. to breakeven)
        'minStrike': 0
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
