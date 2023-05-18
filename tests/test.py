import unittest
from unittest.mock import patch, MagicMock
import api
import json
import cc
import os

from tinydb import TinyDB, Query


class MockApi:
    def __init__(self, apiKey, apiRedirectUri):
        pass

    def connect(self):
        pass

    def getATMPrice(self, asset):
        if asset.startswith('QQQ_TEST'):
            return 8.00

        return 404

    def getOptionChain(self, asset, strikes, date, daysLessAllowed):
        f = open('data/test_chain.json')

        data = json.load(f)

        f.close()

        return data

    def optionExecutionWindowOpen(self):
        return True

    def writeNewContracts(self, oldSymbol, oldAmount, oldDebit, newSymbol, newAmount, newCredit, fullPricePercentage):
        return 123

    def checkOrder(self, orderId):
        return {
            'filled': True,
            'price': 1337,
            'typeAdjustedPrice': 1337,
            'partialFills': 0,
            'complexOrderStrategyType': None,
            'orderType': 'CREDIT'
        }

    def cancelOrder(self, orderId):
        pass

    def checkAccountHasEnoughToCover(self, asset, existingSymbol, amountWillBuyBack, amountToCover, optionStrikeToCover, optionDateToCover):
        return True


class MockApi2(MockApi):
    def getOptionChain(self, asset, strikes, date, daysLessAllowed):
        f = open('data/test_chain_roll_without_debit_min_yield.json')

        data = json.load(f)

        f.close()

        return data


class MockApiPartialFill(MockApi):
    mockFailed = False

    def checkOrder(self, orderId):
        if self.mockFailed:
            self.mockFailed = False
            return {
                'filled': True,
                'price': 1337,
                'typeAdjustedPrice': 1337,
                'partialFills': 0,
                'complexOrderStrategyType': 'DIAGONAL',
                'orderType': 'CREDIT'
            }
        else:
            return {
                'filled': False,
                'price': 1337,
                'typeAdjustedPrice': 1337,
                'partialFills': 1,
                'complexOrderStrategyType': 'DIAGONAL',
                'orderType': 'CREDIT'
            }

    def cancelOrder(self, orderId):
        self.mockFailed = True

    def getOptionChain(self, asset, strikes, date, daysLessAllowed):
        f = open('data/test_chain_partial_fill.json')

        data = json.load(f)

        f.close()

        return data


class MockResponse:
    def __init__(self, data, status_code):
        self.data = data
        self.status_code = status_code

    def json(self):
        return self.data


class MockConnectClientCoverageApi:
    def get_account(self, account_id=None, fields=None):
        f = open('data/test_account.json')

        data = json.load(f)

        f.close()

        return MockResponse(data, 200)

    def get_quote(self, symbol=None):
        f = open('data/test_quote_oqq_option.json')

        data = json.load(f)

        f.close()

        return MockResponse(data, 200)


mockConfig = {
    'QQQ': {
        'amountOfHundreds': 1,
        'minGapToATM': 1,
        'minStrike': 0,
        'deepITMLimit': 10,
        'maxRollupGap': 0,
        'maxDrawdownGap': 10
    }
}

mockConfigTest2 = {
    'QQQ': {
        'amountOfHundreds': 1,
        'minGapToATM': 1,
        'minStrike': 0,
        'deepITMLimit': 10,
        'maxRollupGap': 0,
        'maxDrawdownGap': 10
    }
}

mockConfigPartialFill = {
    'QQQ': {
        'amountOfHundreds': 2,
        'minGapToATM': 1,
        'minStrike': 0,
        'deepITMLimit': 10,
        'maxRollupGap': 0,
        'maxDrawdownGap': 10
    }
}

mockDBTest2 = {"stockSymbol": "QQQ", "optionSymbol": "QQQ_TEST2_400", "expiration": "2021-11-22", "count": 1, "strike": 400.0, "receivedPremium": 8.00}
mockDBPartialFill = {"stockSymbol": "QQQ", "optionSymbol": "QQQ_TEST2_404", "expiration": "2021-11-22", "count": 2, "strike": 404.0, "receivedPremium": 8.00}

dbName = 'testdb.json'


class ApiTestCase(unittest.TestCase):
    @patch('api.Api', MockApi)
    @patch.dict('cc.configuration', mockConfig)
    @patch('cc.dbName', dbName)
    @patch('alert.botAlert', 'console')
    def test_everything(self):
        apiObj = api.Api('123', '456')

        cc.writeCcs(apiObj)
        os.remove(dbName)

    @patch('api.Api', MockApi2)
    @patch.dict('cc.configuration', mockConfigTest2)
    @patch('cc.dbName', dbName)
    @patch('alert.botAlert', 'console')
    def test_roll_without_debit_min_yield(self):
        apiObj = api.Api('123', '456')

        # existing contract in db with ITM strike 400 and premium 8.00
        db = TinyDB(dbName)
        db.insert(mockDBTest2)
        db.close()

        # bot wants to write 405 but only gives 7.00 premium
        # runs into second function which should return the highest strike
        # between 400 - 405 which gives 8.00 premium = 404

        cc.writeCcs(apiObj)
        os.remove(dbName)

    @patch('api.Api', MockApiPartialFill)
    @patch.dict('cc.configuration', mockConfigPartialFill)
    @patch('cc.dbName', dbName)
    @patch('alert.botAlert', 'console')
    def test_partial_fills(self):
        # complexOrderStrategyType = DIAGONAL, amount = 2 pf = 1 then pf = 0 after 1 fail

        apiObj = api.Api('123', '456')

        # existing contract in db with strike 404 and premium 8.00
        db = TinyDB(dbName)
        db.insert(mockDBPartialFill)
        db.close()

        cc.writeCcs(apiObj)

        db = TinyDB(dbName)
        ret = db.search(Query().stockSymbol == 'QQQ')
        db.close()

        assert ret[0]['count'] == 2

        os.remove(dbName)

    @patch('api.Api.connectClient', MockConnectClientCoverageApi)
    @patch('alert.botAlert', 'console')
    @patch('api.ameritradeAccountId', '11111')
    def test_coverage_api(self):
        apiObj = api.Api('123', '456')

        # test acc has 100 shares and 1 itm call (300 strike)
        ret = apiObj.checkAccountHasEnoughToCover('QQQ', 'QQQ_TESTC400', 2, 3, 400.0, '2021-11-23')
        assert ret == False

        ret = apiObj.checkAccountHasEnoughToCover('QQQ', 'QQQ_TESTC400', 2, 2, 400.0, '2021-11-23')
        assert ret == True

        ret = apiObj.checkAccountHasEnoughToCover('QQQ', None, 2, 2, 400.0, '2021-11-23')
        assert ret == True

        ret = apiObj.checkAccountHasEnoughToCover('QQQ', 'QQQ_TESTC400', 2, 2, 300.0, '2021-11-23')
        assert ret == False

        ret = apiObj.checkAccountHasEnoughToCover('QQQ', 'QQQ_TESTC400', 2, 2, 400.0, '2222-22-22')
        assert ret == False

        # in case we had an early assignment or an exit after a partial fill
        # which leaves us with one too few short cc's in the acc (requires manual intervention)
        self.assertRaises(SystemExit, apiObj.checkAccountHasEnoughToCover, 'QQQ', 'QQQ_TESTC400', 3, 3, 400.0, '2021-11-23')


unittest.main()
