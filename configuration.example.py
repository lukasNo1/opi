apiKey = ''
apiRedirectUri = ''
ameritradeAccountId = ''

dbName = 'db.json'

# console, email
botErrorAlert = 'console'

configuration = {
    'QQQ': {
        # how many cc's to write
        'amountOfHundreds': 1,

        # only buy cc's at or over current asset price + this value
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
        'rollWithoutDebit': True,

        # console, email ### what should happen if the bot can't find a cc with the given configuration to write
        'writeRequirementsNotMetAlert': 'console'
    }
}

# don't touch these
debugMarketOpen = False
debugEverythingNeedsRolling = False
debugCanSendOrders = True
