import os
import tda
from webdriver_manager.chrome import ChromeDriverManager
import json
import datetime


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

        # try:
        start = data['option']['EQO']['sessionHours']['regularMarket'][0]['start']
        end = data['option']['EQO']['sessionHours']['regularMarket'][0]['end']

        start = datetime.datetime.fromisoformat(start)
        end = datetime.datetime.fromisoformat(end)

        if start <= date <= end:
            return True
        else:
            return False
        # except (KeyError, TypeError, ValueError):
        #     return False
