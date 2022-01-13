from statistics import median
from support import validDateFormat
import alert


class OptionChain:
    strikes = 24

    def __init__(self, api, asset, days, daysSpread):
        self.api = api
        self.asset = asset
        self.days = days
        self.daysSpread = daysSpread

    def get(self):
        apiData = self.api.getOptionChain(self.asset, self.strikes, self.days, self.daysSpread)

        return self.mapApiData(apiData)

    def mapApiData(self, data):
        # convert api response to data the application can read
        map = []

        try:
            tmp = data['callExpDateMap']
            for key, value in tmp.items():
                split = key.split(':')

                date = split[0]
                days = int(split[1])

                if not validDateFormat(date):
                    return alert.botFailed(self.asset, 'Incorrect date format from api: ' + date)

                contracts = []

                for contractKey, contractValue in value.items():
                    contracts.extend([
                        {
                            'symbol': contractValue[0]['symbol'],
                            'strike': contractValue[0]['strikePrice'],
                            'bid': contractValue[0]['bid'],
                            'ask': contractValue[0]['ask'],
                        }
                    ])

                map.extend([
                    {
                        'date': date,
                        'days': days,
                        'contracts': contracts
                    }
                ])

        except KeyError:
            return alert.botFailed(self.asset, 'Wrong data from api')

        return map

    def sortDateChain(self, chain):
        # ensure this is sorted by strike
        return sorted(chain, key=lambda d: d['strike'])

    def getContractFromDateChain(self, strike, chain):
        chain = self.sortDateChain(chain)

        # get first contract at or above strike
        for contract in chain:
            if contract['strike'] >= strike:
                return contract

        return None

    def getContractFromDateChainByMinYield(self, minStrike, maxStrike, minYield, chain):
        chain = self.sortDateChain(chain)

        # highest strike to lowest
        for contract in reversed(chain):
            if contract['strike'] > maxStrike:
                continue

            if contract['strike'] < minStrike:
                break

            if median([contract['bid'], contract['ask']]) >= minYield:
                return contract

        return None

