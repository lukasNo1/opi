from configuration import configuration, dbName, debugEverythingNeedsRolling
from optionChain import OptionChain
from statistics import median
from tinydb import TinyDB, Query
import datetime
import time
import alert
import support


class Cc:

    def __init__(self, asset):
        self.asset = asset

    def findNew(self, api, existing, existingPremium):
        asset = self.asset

        newccExpDate = support.getNewCcExpirationDate()

        # get option chain of third thursday and friday of the month
        optionChain = OptionChain(api, asset, newccExpDate, 1)

        chain = optionChain.get()

        if not chain:
            return alert.botFailed(asset, 'No chain found on the third thursday OR friday')

        # get closest chain to days
        # it will get friday most of the time, but if a friday is a holiday f.ex. the chain will only return a thursday date chain
        closestChain = chain[-1]

        atmPrice = api.getATMPrice(asset)
        strikePrice = atmPrice + configuration[asset]['minGapToATM']

        minStrike = configuration[asset]['minStrike']

        if existing:
            maxDrawdownStrike = existing['strike'] - configuration[asset]['maxDrawdownGap']
        else:
            maxDrawdownStrike = None

        if maxDrawdownStrike and maxDrawdownStrike > strikePrice:
            print('Applying max drawdown (' + str(maxDrawdownStrike) + ') ...')
            strikePrice = maxDrawdownStrike

        if minStrike > strikePrice:
            print('Min strike hit, applying (' + str(minStrike) + ') ...')
            strikePrice = minStrike

        #  get the best matching contract
        contract = optionChain.getContractFromDateChain(strikePrice, closestChain['contracts'])

        if not contract:
            return alert.botFailed(asset, 'No contract over minStrike found')

        # check minYield
        projectedPremium = median([contract['bid'], contract['ask']])

        if projectedPremium < existingPremium:
            if existing:
                print('Failed to write contract for CREDIT with CC (' + str(contract['strike']) + '), now trying to get a lower strike ...')

                # we need to get a lower strike instead to not pay debit
                contract = optionChain.getContractFromDateChainByMinYield(existing['strike'], strikePrice, existingPremium, closestChain['contracts'])

                # edge case where this new contract fails: If even a calendar roll wouldn't result in a credit
                if not contract:
                    return alert.botFailed(asset, 'couldn\'t find contract for CREDIT above last strike price')

                #  allow to pay for roll up if we are too far itm
                if configuration[asset]['deepITMRollupGap'] > 0 and self.tooFarItm(contract['strike'], atmPrice):
                    rollUpStrike = existing['strike'] + configuration[asset]['deepITMRollupGap']

                    # rollUpStrike is possibly still too far itm, but we are not gonna roll up more than this
                    print('Could roll to ' + str(contract['strike']) + ' for CREDIT, but its too far ITM ...')
                    print('Rolling to deepITMRollupGap instead (' + str(rollUpStrike) + '), paying debit ...')
                    contract = optionChain.getContractFromDateChain(rollUpStrike, closestChain['contracts'])
                    # todo should we check if the account has enough cash to rollup to this contract?

                projectedPremium = median([contract['bid'], contract['ask']])
            else:
                return alert.botFailed(asset, 'Api / code error: No existing contract and projected premium for ' +
                                       str(strikePrice) + ' is smaller than ' + str(existingPremium))

        return {
            'date': closestChain['date'],
            'days': closestChain['days'],
            'contract': contract,
            'projectedPremium': projectedPremium
        }

    def tooFarItm(self, newStrike, atmPrice):
        return newStrike < atmPrice - configuration[self.asset]['deepITMLimit']

    def existing(self):
        db = TinyDB(dbName)
        ret = db.search(Query().stockSymbol == self.asset)
        db.close()

        return ret


def writeCcs(api):
    for asset in configuration:
        asset = asset.upper()
        cc = Cc(asset)

        try:
            existing = cc.existing()[0]
        except IndexError:
            existing = None

        if (existing and needsRolling(existing)) or not existing:
            amountToSell = configuration[asset]['amountOfHundreds']

            if existing:
                existingSymbol = existing['optionSymbol']
                amountToBuyBack = existing['count']
                existingPremium = api.getATMPrice(existing['optionSymbol'])
            else:
                existingSymbol = None
                amountToBuyBack = 0
                existingPremium = 0

            new = cc.findNew(api, existing, existingPremium)

            print('The bot wants to write the following contract:')
            print(new)

            if not api.checkAccountHasEnoughToCover(asset, existingSymbol, amountToBuyBack, amountToSell, new['contract']['strike'], new['date']):
                return alert.botFailed(asset, 'The account doesn\'t have enough shares or options to cover selling '
                                       + str(amountToSell) + ' cc(\'s)')

            writeCc(api, asset, new, existing, existingPremium, amountToBuyBack, amountToSell)
        else:
            print('Nothing to write ...')


def needsRolling(cc):
    if debugEverythingNeedsRolling:
        return True

    # needs rolling on date BEFORE expiration (if the market is closed, it will trigger ON expiration date)
    nowPlusOffset = (datetime.datetime.utcnow() + datetime.timedelta(days=support.ccExpDaysOffset)).strftime('%Y-%m-%d')

    return nowPlusOffset >= cc['expiration']


def writeCc(api, asset, new, existing, existingPremium, amountToBuyBack, amountToSell, retry=0, partialContractsSold=0):
    maxRetries = 50
    # lower the price by 1% for each retry if we couldn't get filled
    orderPricePercentage = 100 - retry

    if retry > maxRetries:
        return alert.botFailed(asset, 'Order cant be filled, tried with ' + str(orderPricePercentage + 1) + '% of the price.')

    if existing and existingPremium:
        orderId = api.writeNewContracts(
            existing['optionSymbol'],
            amountToBuyBack,
            existingPremium,
            new['contract']['symbol'],
            amountToSell,
            new['projectedPremium'],
            orderPricePercentage
        )
    else:
        orderId = api.writeNewContracts(
            None,
            0,
            0,
            new['contract']['symbol'],
            amountToSell,
            new['projectedPremium'],
            orderPricePercentage
        )

    checkFillXTimes = 12

    if retry > 0:
        # go faster through it
        checkFillXTimes = 6

    for x in range(checkFillXTimes):
        # try to fill it for x * 5 seconds
        print('Waiting for order to be filled ...')

        time.sleep(5)

        checkedOrder = api.checkOrder(orderId)

        if checkedOrder['filled']:
            print('Order has been filled!')
            break

    if not checkedOrder['filled']:
        api.cancelOrder(orderId)

        print('Cant fill order, retrying with lower price ...')

        if checkedOrder['partialFills'] > 0:
            if checkedOrder['complexOrderStrategyType'] is None or (checkedOrder['complexOrderStrategyType'] and checkedOrder['complexOrderStrategyType'] != 'DIAGONAL'):
                # partial fills are only possible on DIAGONAL orders, so this should never happen
                return alert.botFailed(asset, 'Partial fill on custom order, manual review required: ' + str(checkedOrder['partialFills']))

            # on diagonal fill is per leg, 1 fill = 1 bought back and 1 sold

            # quick verification, this should never be true
            if not (amountToBuyBack == amountToSell and amountToBuyBack > checkedOrder['partialFills']):
                return alert.botFailed(asset, 'Partial fill amounts do not match, manual review required')

            diagonalAmountBothWays = amountToBuyBack - checkedOrder['partialFills']

            receivedPremium = checkedOrder['price'] * checkedOrder['partialFills']

            alert.alert(asset, 'Partial fill: Bought back ' + str(checkedOrder['partialFills']) + 'x ' + existing['optionSymbol'] + ' and sold ' + str(
                checkedOrder['partialFills']) + 'x ' +
                        new['contract']['symbol'] + ' for ' + str(receivedPremium))

            return writeCc(api, asset, new, existing, existingPremium, diagonalAmountBothWays, diagonalAmountBothWays, retry + 1,
                           partialContractsSold + checkedOrder['partialFills'])

        return writeCc(api, asset, new, existing, existingPremium, amountToBuyBack, amountToSell, retry + 1, partialContractsSold)

    receivedPremium = checkedOrder['price'] * amountToSell

    if existing:
        if amountToBuyBack != amountToSell:
            # custom order, price is not per contract
            receivedPremium = checkedOrder['price']

        alert.alert(asset, 'Bought back ' + str(amountToBuyBack) + 'x ' + existing['optionSymbol'] + ' and sold ' + str(amountToSell) + 'x ' +
                    new['contract']['symbol'] + ' for ' + str(receivedPremium))
    else:
        alert.alert(asset, 'Sold ' + str(amountToSell) + 'x ' + new['contract']['symbol'] + ' for ' + str(receivedPremium))

    if partialContractsSold > 0:
        amountHasSold = partialContractsSold + amountToSell
        receivedPremium = receivedPremium + checkedOrder['price'] * partialContractsSold

        # shouldn't happen
        if amountHasSold != configuration[asset]['amountOfHundreds']:
            return alert.botFailed(asset, 'Unexpected amount of contracts sold: ' + str(amountHasSold))
    else:
        amountHasSold = amountToSell

    soldOption = {
        'stockSymbol': asset,
        'optionSymbol': new['contract']['symbol'],
        'expiration': new['date'],
        'count': amountHasSold,
        'strike': new['contract']['strike'],
        'receivedPremium': receivedPremium
    }

    db = TinyDB(dbName)

    db.remove(Query().stockSymbol == asset)
    db.insert(soldOption)

    db.close()

    return soldOption
