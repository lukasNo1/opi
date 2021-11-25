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

                date = split[0]  # todo ensure yyyy-mm-dd
                days = int(split[1])

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
            # todo better exception handling
            print('wrong data from api')
            exit(1)

        return map

    def getContractFromDateChain(self, strike, chain):
        # ensure this is sorted by strike
        chain = sorted(chain, key=lambda d: d['strike'])

        # get first contract at or above strike
        for contract in chain:
            if contract['strike'] >= strike:
                return contract

        return None
