from configuration import configuration, dbName
from optionChain import OptionChain
from statistics import median
from tinydb import TinyDB, Query
import datetime


class Cc:

    def __init__(self, asset):
        self.asset = asset

    def findNew(self, api, existing):
        asset = self.asset

        optionChain = OptionChain(api, asset, configuration[asset]['days'], configuration[asset]['daysSpread'])

        chain = optionChain.get()
        # todo handle no chain found

        # get closest chain to days
        closestChain = min(chain, key=lambda x: abs(x['days'] - configuration[asset]['days']))

        # note: if the days or days - daysSpread in configuration amount to less than 3, date will always be too close
        # (with daysSpread only if it round down instead of up to get the best contract)
        dateTooClose = closestChain['days'] < 3 or abs(closestChain['days'] - configuration[asset]['days']) < -configuration[asset]['daysSpread']
        dateTooFaar = abs(closestChain['days'] - configuration[asset]['days']) > configuration[asset]['daysSpread']

        minStrike = configuration[asset]['minStrike']
        atmPrice = 0

        # check if its within the spread
        if dateTooClose or dateTooFaar:
            return writingCcFailed('days range')

        #  get the best matching contract
        if configuration[asset]['rollCalendar']:
            if not existing:
                return writingCcFailed('roll calendar selected but no option to roll')

            # this technically allows a strike greater than the current one if none other available, which wouldn't be a calendar roll
            # this can be bad on a chain with few options, but we have to roll something, can't let it expire
            minStrike = existing['strike']
            strikePrice = existing['strike']
        else:
            atmPrice = api.getATMPrice(asset)
            strikePrice = atmPrice + configuration[asset]['minGapToATM']

            if minStrike < atmPrice:
                minStrike = atmPrice

        contract = optionChain.getContractFromDateChain(strikePrice, closestChain['contracts'])

        if not contract or (not configuration[asset]['rollCalendar'] and contract['strike'] < minStrike):
            return writingCcFailed('minStrike')

        # check minYield
        projectedPremium = median([contract['bid'], contract['ask']]) * 100

        if not configuration[asset]['rollCalendar'] and projectedPremium < configuration[asset]['minYield']:
            return writingCcFailed('minYield')

        return {
            'date': closestChain['date'],
            'days': closestChain['days'],
            'contract': contract,
            'projectedPremium': projectedPremium
        }

    def existing(self):
        # todo refactor
        db = TinyDB(dbName)

        return db.search(Query().stockSymbol == self.asset)


def writeCcs(api):
    for asset in configuration:
        asset = asset.upper()
        cc = Cc(asset)

        try:
            existing = cc.existing()[0]
        except IndexError:
            existing = None

        if (existing and needsRolling(existing)) or not existing:
            new = cc.findNew(api, existing)

            print('The bot wants to write the following contract:')
            print(new)

            writeCc(api, asset, new, existing)
        else:
            print('Nothing to write ...')


def needsRolling(cc):
    # needs rolling on date BEFORE expiration (if the market is closed, it will trigger ON expiration date)
    daysOffset = 1
    nowPlusOffset = (datetime.datetime.utcnow() + datetime.timedelta(days=daysOffset)).strftime('%Y-%m-%d')

    return nowPlusOffset >= cc['expiration']


def writeCc(api, asset, new, existing):
    # todo api, roll if existing, else just normal order
    # Client.place_order(account_id, order_spec)
    # tda.utils.Utils.extract_order_id()
    # Client.get_order(order_id, account_id)

    soldOption = {
        'stockSymbol': asset,
        'optionSymbol': new['contract']['symbol'],
        'expiration': new['date'],
        'count': -1,
        'strike': new['contract']['strike'],
        'receivedPremium': 0
    }

    # todo refactor
    db = TinyDB(dbName)

    # todo remove/update only if roll
    db.remove(Query().stockSymbol == asset)
    db.insert(soldOption)

    return soldOption


def writingCcFailed(message):
    # todo throw according to writeRequirementsNotMetAlert
    print(message)
    exit(1)
