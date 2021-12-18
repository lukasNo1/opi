apiKey = ''
apiRedirectUri = ''
ameritradeAccountId = ''

dbName = 'db.json'

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
        'minYield': 300,

        # if we need to roll, only roll calendar (OVERWRITES minGapToATM, minStrike and minYield!!!)
        'rollCalendar': False,

        # None, email ### what should happen if the bot can't find a cc with the given configuration to write
        'writeRequirementsNotMetAlert': None
    }
}



# don't touch these
debugMarketOpen = False
debugEverythingNeedsRolling = False
debugCanSendOrders = True
