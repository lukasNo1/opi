from configuration import configuration, apiKey, apiRedirectUri, dbName
from optionChain import OptionChain
from api import Api
from statistics import median
from tinydb import TinyDB, Query


class Cc:

    def __init__(self, asset):
        self.asset = asset

    def findNew(self, existing):
        asset = self.asset

        api = Api(apiKey, apiRedirectUri)
        api.connect()

        optionChain = OptionChain(api, asset, configuration[asset]['days'], configuration[asset]['daysSpread'])

        chain = optionChain.get()
        # todo handle no chain found

        # get closest chain to days
        closestChain = min(chain, key=lambda x: abs(x['days'] - configuration[asset]['days']))

        # note: if the days or days - daysSpread in configuration amount to less than 3, date will always be too close
        # (with daysSpread only if it round down instead of up to get the best contract)
        dateTooClose = closestChain['days'] < 3 or abs(closestChain['days'] - configuration[asset]['days']) < -configuration[asset]['daysSpread']
        dateTooFaar = abs(closestChain['days'] - configuration[asset]['days']) > configuration[asset]['daysSpread']

        # check if its within the spread
        if dateTooClose or dateTooFaar:
            return writingCcFailed('days range')

        #  get the best matching contract
        if configuration[asset]['rollCalendar']:
            # todo strike of last option, fail if it doesnt have one
            atmPrice = 0
            strikePrice = 0
        else:
            atmPrice = api.getATMPrice(asset)
            strikePrice = atmPrice + configuration[asset]['minGapToATM']

        # todo get closest contract ABOVE strikePrice instead of closest value above or below
        contract = optionChain.getContractFromDateChain(strikePrice, closestChain['contracts'])

        minStrike = configuration[asset]['minStrike']

        # todo if we have a option we are rolling, use the options price as minStrike
        if minStrike < atmPrice:
            minStrike = atmPrice

        if not configuration[asset]['rollCalendar'] and contract['strike'] < minStrike:
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


def writeCcs():
    for asset in configuration:
        asset = asset.upper()
        cc = Cc(asset)

        try:
            existing = cc.existing()[0]
        except IndexError:
            existing = None

        if (existing and needsRolling(existing)) or not existing:
            new = cc.findNew(existing)

            print('The bot wants to write the following contract:')
            print(new)
            writeCc(asset, new)
        else:
            print('Nothing to write ...')


def needsRolling(cc):
    # todo
    return True


def writeCc(asset, cc):
    # todo api
    # Client.place_order(account_id, order_spec)
    # tda.utils.Utils.extract_order_id()
    # Client.get_order(order_id, account_id)

    soldOption = {
        'stockSymbol': asset,
        'optionSymbol': cc['contract']['symbol'],
        'expiration': cc['date'],
        'count': -1,
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
