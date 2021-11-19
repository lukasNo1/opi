from configuration import configuration
from statistics import median
import sys


def findCC(asset):
    allowedDaysRange = configuration[asset]['days'] + configuration[asset]['daysSpread']
    chain = getOptionChain(asset, allowedDaysRange)
    # todo handle no chain found

    # get closest chain to days
    closestChain = min(chain, key=lambda x: abs(x['days'] - configuration[asset]['days']))

    dateTooClose = abs(closestChain['days'] - configuration[asset]['days']) < -configuration[asset]['daysSpread']
    dateTooFaar = abs(closestChain['days'] - configuration[asset]['days']) > configuration[asset]['daysSpread']

    # check if its within the spread
    if dateTooClose or dateTooFaar:
        return writingCcFailed('date range')

    #  get the best matching contract
    if configuration[asset]['rollCalendar']:
        # todo strike of last option, fail if it doesnt have one
        strikePrice = 0
    else:
        strikePrice = getATMPrice() + configuration[asset]['minGapToATM']

    contract = getContractFromChain(strikePrice, closestChain['contracts'])

    # check minYield
    projectedPremium = median([contract['bid'], contract['ask']])

    if not configuration[asset]['rollCalendar'] and projectedPremium < configuration[asset]['minYield']:
        return writingCcFailed('minYield')

    return {
        'days': closestChain['days'],
        'contract': contract,
        'projectedPremium': projectedPremium
    }


def getContractFromChain(strike, chain):
    return min(chain, key=lambda x: abs(x['strike'] - strike))


def getATMPrice():
    # todo api
    return 150


def getOptionChain(asset, daysOut):
    strikes = 24
    # todo api
    return [
        {
            'days': 28,
            'contracts': [
                {
                    'strike': 150,
                    'bid': 100,
                    'ask': 101
                }
            ]
        },
        {
            'days': 31,
            'contracts': [
                {
                    'strike': 150,
                    'bid': 100,
                    'ask': 101
                },
                {
                    'strike': 151,
                    'bid': 300,
                    'ask': 301
                }
            ]
        }
    ]


def writingCcFailed(message):
    # todo throw according to writeRequirementsNotMetAlert
    print(message)
    sys.exit(1)


def writeCcs():
    for asset in configuration:
        cc = findCC(asset)

        print('The bot wants to write the following contract:')
        print(cc)

        # writeCc(cc)


def writeCc(cc):
    # todo api
    return True


# todo
# infinite loop, check written contracts if we need to sell them

writeCcs()
