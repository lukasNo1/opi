import os
from tda import auth, client
from webdriver_manager.chrome import ChromeDriverManager
import json


class Api:
    client = None
    tokenPath = ''
    apiKey = ''
    apiRedirectUri = ''

    def __init__(self, apiKey, apiRedirectUri):
        self.tokenPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')
        self.apiKey = apiKey
        self.apiRedirectUri = apiRedirectUri

    def connect(self):
        try:
            self.client = auth.client_from_token_file(self.tokenPath, self.apiKey)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(ChromeDriverManager().install()) as driver:
                self.client = auth.client_from_login_flow(
                    driver, self.apiKey, self.apiRedirectUri, self.tokenPath)

    def getATMPrice(self, asset):
        # client can be None
        r = self.client.get_quote(asset)

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
