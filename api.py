import math
import os
import tda
from tda.utils import Utils
from webdriver_manager.chrome import ChromeDriverManager
from configuration import ameritradeAccountId, debugCanSendOrders
import datetime
from statistics import median
import alert
from support import validDateFormat


class Api:
    connectClient = None
    tokenPath = ''
    apiKey = ''
    apiRedirectUri = ''

    def __init__(self, apiKey, apiRedirectUri):
        self.tokenPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')
        self.apiKey = apiKey
        self.apiRedirectUri = apiRedirectUri

    def setup(self):
        from selenium import webdriver
        with webdriver.Chrome(ChromeDriverManager().install()) as driver:
            self.connectClient = tda.auth.client_from_login_flow(
                driver, self.apiKey, self.apiRedirectUri, self.tokenPath)

    def connect(self):
        try:
            self.connectClient = tda.auth.client_from_token_file(self.tokenPath, self.apiKey)
        except FileNotFoundError:
            return alert.botFailed(None, 'Manual authentication required, run setupApi.py first.')

    def getATMPrice(self, asset):
        # client can be None
        r = self.connectClient.get_quote(asset)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()
        lastPrice = 0

        try:
            if data[asset]['assetType'] == 'OPTION':
                lastPrice = median([data[asset]['bidPrice'], data[asset]['askPrice']])
            else:
                lastPrice = data[asset]['lastPrice']
        except KeyError:
            return alert.botFailed(asset, 'Wrong data from api when getting ATM price')

        return lastPrice

    def getOptionChain(self, asset, strikes, date, daysLessAllowed):
        fromDate = date - datetime.timedelta(days=daysLessAllowed)
        toDate = date

        r = self.connectClient.get_option_chain(
            asset,
            contract_type=self.connectClient.Options.ContractType.CALL,
            strike_count=strikes,
            include_quotes='TRUE',
            strategy=self.connectClient.Options.Strategy.SINGLE,
            interval=None,
            strike=None,
            strike_range=None,
            from_date=fromDate,
            to_date=toDate,
            volatility=None,
            underlying_price=None,
            interest_rate=None,
            days_to_expiration=None,
            exp_month=None,
            option_type=None
        )

        assert r.status_code == 200, r.raise_for_status()

        return r.json()

    def getOptionExecutionWindow(self):
        now = datetime.datetime.utcnow()
        now = now.replace(tzinfo=datetime.timezone.utc)

        r = self.connectClient.get_hours_for_single_market(tda.client.Client.Markets.OPTION, now)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        try:
            marketKey = list(data['option'].keys())[0]

            sessionHours = data['option'][marketKey]['sessionHours']

            if sessionHours is None:
                # the market is closed today
                return {
                    'open': False,
                    'openDate': None,
                    'nowDate': now
                }

            end = sessionHours['regularMarket'][0]['end']

            end = datetime.datetime.fromisoformat(end)
            # execute during the last open hour
            start = end - datetime.timedelta(hours=1)

            if start <= now <= end:
                return {
                    'open': True,
                    'openDate': start,
                    'nowDate': now
                }
            else:
                return {
                    'open': False,
                    'openDate': start,
                    'nowDate': now
                }
        except (KeyError, TypeError, ValueError):
            return alert.botFailed(None, 'Error getting the market hours for today.')

    def writeNewContracts(self, oldSymbol, oldAmount, oldDebit, newSymbol, newAmount, newCredit, fullPricePercentage):
        """
           Send an order for writing new contracts to the api
           fullPricePercentage is for reducing the price by a custom amount if we cant get filled
       """

        if oldSymbol is None:
            price = newCredit * (fullPricePercentage / 100)

            # init a new position, sell to open
            order = tda.orders.options.option_sell_to_open_limit(newSymbol, newAmount, price) \
                .set_duration(tda.orders.common.Duration.DAY) \
                .set_session(tda.orders.common.Session.NORMAL) \
                .set_special_instruction(tda.orders.common.SpecialInstruction.ALL_OR_NONE)
        else:
            # roll
            price = -((oldDebit * oldAmount - newCredit * newAmount) * (fullPricePercentage / 100))
            order = tda.orders.generic.OrderBuilder()

            orderType = tda.orders.common.OrderType.NET_CREDIT

            if price < 0:
                price = -price
                orderType = tda.orders.common.OrderType.NET_DEBIT

            order.add_option_leg(tda.orders.common.OptionInstruction.BUY_TO_CLOSE, oldSymbol, oldAmount) \
                .add_option_leg(tda.orders.common.OptionInstruction.SELL_TO_OPEN, newSymbol, newAmount) \
                .set_duration(tda.orders.common.Duration.DAY) \
                .set_session(tda.orders.common.Session.NORMAL) \
                .set_price(price) \
                .set_order_type(orderType) \
                .set_order_strategy_type(tda.orders.common.OrderStrategyType.SINGLE) \
                .set_special_instruction(tda.orders.common.SpecialInstruction.ALL_OR_NONE)

        if not debugCanSendOrders:
            print(order.build())
            exit()

        r = self.connectClient.place_order(ameritradeAccountId, order)

        order_id = Utils(self.connectClient, ameritradeAccountId).extract_order_id(r)
        assert order_id is not None

        return order_id

    def checkOrder(self, orderId):
        r = self.connectClient.get_order(orderId, ameritradeAccountId)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        try:
            filled = data['status'] == 'FILLED'
            price = data['price']
        except KeyError:
            return alert.botFailed(None, 'Error while checking working order')

        return {
            'filled': filled,
            'price': price
        }

    def cancelOrder(self, orderId):
        r = self.connectClient.cancel_order(orderId, ameritradeAccountId)

        # throws error if cant cancel (code 400 - 404)
        assert r.status_code == 200, r.raise_for_status()

    def checkAccountHasEnoughToCover(self, asset, existingSymbol, amountWillBuyBack, amountToCover, optionStrikeToCover, optionDateToCover):
        # we check here if the user has
        # amountOfHundreds * 100 shares or amountOfHundreds options lower than new strike in acc (and further out)
        r = self.connectClient.get_account(ameritradeAccountId, fields=tda.client.Client.Account.Fields.POSITIONS)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        if existingSymbol and not self.checkPreviousSoldCcsStillHere(existingSymbol, amountWillBuyBack, data):
            # something bad happened, let the user know he needs to look into it
            return alert.botFailed(asset, 'The cc\'s the bot wants to buy back aren\'t in the account anymore, manual review required.')

        # set to this instead of 0 because we ignore the amount of options the bot has sold itself, as we are buying them back
        coverage = amountWillBuyBack

        try:
            for position in data['securitiesAccount']['positions']:
                if position['instrument']['assetType'] == 'EQUITY' and position['instrument']['symbol'] == asset:
                    amountOpen = int(position['longQuantity']) - int(position['shortQuantity'])

                    # can be less than 0, removes coverage then
                    coverage += math.floor(amountOpen / 100)

                if position['instrument']['assetType'] == 'OPTION' and position['instrument']['underlyingSymbol'] == asset and position['instrument']['putCall'] == 'CALL':
                    optionData = self.getOptionExpirationDateAndStrike(position['instrument']['symbol'])
                    strike = optionData['strike']
                    optionDate = optionData['expiration']
                    amountOpen = int(position['longQuantity']) - int(position['shortQuantity'])

                    if amountOpen > 0 and (strike >= optionStrikeToCover or optionDate < optionDateToCover):
                        # we cant cover with this, so we dont add it to coverage if its positive,
                        # but we substract when negative
                        continue

                    coverage += amountOpen

            return coverage >= amountToCover

        except KeyError:
            return alert.botFailed(asset, 'Error while checking the account coverage')

    def checkPreviousSoldCcsStillHere(self, asset, amount, data):
        """
        Check if we still have the amount of cc's we sold in the account
        If not, then something bad happened like early assignment f.ex.
        """
        try:
            for position in data['securitiesAccount']['positions']:
                if position['instrument']['symbol'] == asset:
                    # we allow there to be MORE sold of this option but not less
                    # Useful f.ex. if someone wants to manually sell more (independent of the bot)
                    return position['shortQuantity'] >= amount and position['longQuantity'] == 0

            return False

        except KeyError:
            return False

    def getOptionExpirationDateAndStrike(self, asset):
        r = self.connectClient.get_quote(asset)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        try:
            year = str(data[asset]['expirationYear'])
            month = str(data[asset]['expirationMonth']).zfill(2)
            day = str(data[asset]['expirationDay']).zfill(2)
            expiration = year + '-' + month + '-' + day

            if not validDateFormat(expiration):
                return alert.botFailed(asset, 'Incorrect date format from api: ' + expiration)

            return {
                'strike': data[asset]['strikePrice'],
                'expiration': expiration
            }
        except KeyError:
            return alert.botFailed(asset, 'Wrong data from api when getting option expiry data')
