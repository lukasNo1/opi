import os
import tda
from tda.utils import Utils
from webdriver_manager.chrome import ChromeDriverManager
from configuration import ameritradeAccountId
import datetime
from statistics import median


class Api:
    connectClient = None
    tokenPath = ''
    apiKey = ''
    apiRedirectUri = ''

    def __init__(self, apiKey, apiRedirectUri):
        self.tokenPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')
        self.apiKey = apiKey
        self.apiRedirectUri = apiRedirectUri

    def connect(self):
        try:
            self.connectClient = tda.auth.client_from_token_file(self.tokenPath, self.apiKey)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(ChromeDriverManager().install()) as driver:
                self.connectClient = tda.auth.client_from_login_flow(
                    driver, self.apiKey, self.apiRedirectUri, self.tokenPath)

    def getATMPrice(self, asset):
        # client can be None
        r = self.connectClient.get_quote(asset)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()
        lastPrice = 0

        try:
            if data[asset]['assetType'] == 'OPTION':
                lastPrice = median([data[asset]['bidPrice'], data[asset]['askPrice']]) * 100
            else:
                lastPrice = data[asset]['lastPrice']
        except KeyError:
            # todo better exception handling
            print('wrong data from api')
            exit(1)

        return lastPrice

    def getOptionChain(self, asset, strikes, days, daysSpread):
        # todo limit dates to get to days +- daysSpread

        r = self.connectClient.get_option_chain(
            asset,
            contract_type=self.connectClient.Options.ContractType.CALL,
            strike_count=strikes,
            include_quotes='TRUE',
            strategy=self.connectClient.Options.Strategy.SINGLE,
            interval=None,
            strike=None,
            strike_range=None,
            from_date=None,
            to_date=None,
            volatility=None,
            underlying_price=None,
            interest_rate=None,
            days_to_expiration=None,
            exp_month=None,
            option_type=None
        )

        assert r.status_code == 200, r.raise_for_status()

        return r.json()

    def isOptionMarketOpen(self):
        date = datetime.datetime.utcnow()
        date = date.replace(tzinfo=datetime.timezone.utc)

        r = self.connectClient.get_hours_for_single_market(tda.client.Client.Markets.OPTION, date)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        try:
            start = data['option']['EQO']['sessionHours']['regularMarket'][0]['start']
            end = data['option']['EQO']['sessionHours']['regularMarket'][0]['end']

            start = datetime.datetime.fromisoformat(start)
            end = datetime.datetime.fromisoformat(end)

            if start <= date <= end:
                return True
            else:
                return False
        except (KeyError, TypeError, ValueError):
            return False

    def writeNewContracts(self, oldSymbol, oldAmount, oldDebit, newSymbol, newAmount, newCredit):
        if oldSymbol is None:
            price = newCredit
            # init a new position, buy to open
            order = tda.orders.options.option_buy_to_open_limit(newSymbol, newAmount, price) \
                .set_duration(tda.orders.common.Duration.DAY) \
                .set_session(tda.orders.common.Session.NORMAL)
        else:
            # roll
            price = oldDebit - newCredit
            order = tda.orders.generic.OrderBuilder()

            order.set_complex_order_strategy_type(tda.orders.common.ComplexOrderStrategyType.DIAGONAL) \
                .add_option_leg(tda.orders.common.OptionInstruction.BUY_TO_CLOSE, oldSymbol, oldAmount) \
                .add_option_leg(tda.orders.common.OptionInstruction.SELL_TO_OPEN, newSymbol, newAmount) \
                .set_duration(tda.orders.common.Duration.DAY) \
                .set_session(tda.orders.common.Session.NORMAL) \
                .set_price(price)

        print(order.build())
        exit()
        # todo uncomment this
        # r = self.connectClient.place_order(ameritradeAccountId, order)
        #
        # assert r.status_code == 200, r.raise_for_status()
        # order_id = Utils(self.connectClient, ameritradeAccountId).extract_order_id(r)
        # assert order_id is not None
        #
        # return order_id

    def checkOrder(self, orderId):
        r = self.connectClient.get_order(orderId, ameritradeAccountId)

        assert r.status_code == 200, r.raise_for_status()

        data = r.json()

        try:
            filled = data['status'] == 'FILLED'
            price = data['price']
        except (KeyError):
            filled = False
            price = 0

        return {
            'filled': filled,
            'price': price
        }

    def cancelOrder(self, orderId):
        r = self.connectClient.cancel_order(orderId, ameritradeAccountId)

        # throws error if cant cancel (code 400 - 404)
        assert r.status_code == 200, r.raise_for_status()
