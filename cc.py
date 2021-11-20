from configuration import configuration
from configuration import apiKey
from configuration import apiRedirectUri
from optionChain import OptionChain
from api import Api
from statistics import median


class Cc:

    def __init__(self, asset):
        self.asset = asset

    def find(self):
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

        contract = optionChain.getContractFromDateChain(strikePrice, closestChain['contracts'])

        minStrike = configuration[asset]['minStrike']

        if minStrike < atmPrice:
            minStrike = atmPrice

        if not configuration[asset]['rollCalendar'] and contract['strike'] < minStrike:
            return writingCcFailed('minStrike')

        # check minYield
        projectedPremium = median([contract['bid'], contract['ask']]) * 100

        if not configuration[asset]['rollCalendar'] and projectedPremium < configuration[asset]['minYield']:
            return writingCcFailed('minYield')

        return {
            'days': closestChain['days'],
            'contract': contract,
            'projectedPremium': projectedPremium
        }


def writeCcs():
    for asset in configuration:
        asset = asset.upper()

        cc = Cc(asset).find()

        print('The bot wants to write the following contract:')
        print(cc)

        # writeCc(cc)


def writeCc(cc):
    # todo api
    return True


def writingCcFailed(message):
    # todo throw according to writeRequirementsNotMetAlert
    print(message)
    exit(1)
