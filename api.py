import os
from tda import auth, client
from webdriver_manager.chrome import ChromeDriverManager
import json


class Api:
    tokenPath = ''
    apiKey = ''
    apiRedirectUri = ''

    def __init__(self, apiKey, apiRedirectUri):
        self.tokenPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')
        self.apiKey = apiKey
        self.apiRedirectUri = apiRedirectUri

    def connect(self):
        try:
            c = auth.client_from_token_file(self.tokenPath, self.apiKey)
        except FileNotFoundError:
            from selenium import webdriver
            with webdriver.Chrome(ChromeDriverManager().install()) as driver:
                c = auth.client_from_login_flow(
                    driver, self.apiKey, self.apiRedirectUri, self.tokenPath)

        # r = c.get_price_history('AAPL',
        #                         period_type=client.Client.PriceHistory.PeriodType.YEAR,
        #                         period=client.Client.PriceHistory.Period.TEN_YEARS,
        #                         frequency_type=client.Client.PriceHistory.FrequencyType.DAILY,
        #                         frequency=client.Client.PriceHistory.Frequency.DAILY)
        # assert r.status_code == 200, r.raise_for_status()
        # print(json.dumps(r.json(), indent=4))

    def getATMPrice(self):
        # todo api
        return 150
