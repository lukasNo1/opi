import unittest
from unittest.mock import patch, MagicMock
import api
import json
import cc
import os


class MockApi:
    def __init__(self, apiKey, apiRedirectUri):
        pass

    def connect(self):
        pass

    def getATMPrice(self, asset):
        return 404

    def getOptionChain(self, asset, strikes, days, daysSpread):
        f = open('data/testChain.json')

        data = json.load(f)

        f.close()

        return data

    def optionExecutionWindowOpen(self):
        return True

    def writeNewContracts(self, oldSymbol, oldAmount, oldDebit, newSymbol, newAmount, newCredit):
        return 123

    def checkOrder(self, orderId):
        return {
            'filled': True,
            'price': 1337
        }

    def cancelOrder(self, orderId):
        pass


mockConfig = {
    'QQQ': {
        'amountOfHundreds': 1,
        'minGapToATM': 1,
        'minStrike': 0,
        'days': 30,
        'daysSpread': 10,
        'minYield': 0,
        'rollCalendar': False,
        'writeRequirementsNotMetAlert': None
    }
}

dbName = 'testdb.json'


class ApiTestCase(unittest.TestCase):
    @patch('api.Api', MockApi)
    @patch.dict('cc.configuration', mockConfig)
    @patch('cc.dbName', dbName)
    def test_everything(self):
        apiObj = api.Api('123', '456')

        cc.writeCcs(apiObj)
        os.remove(dbName)


unittest.main()
