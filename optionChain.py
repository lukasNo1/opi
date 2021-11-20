class OptionChain:
    strikes = 24

    def __init__(self, api, asset, daysOut):
        self.api = api
        self.asset = asset
        self.daysOut = daysOut

    def get(self):
        # todo api
        return [
            {
                'days': 28,
                'contracts': [
                    {
                        'strike': 150,
                        'bid': 100,
                        'ask': 101
                    }
                ]
            },
            {
                'days': 31,
                'contracts': [
                    {
                        'strike': 150,
                        'bid': 100,
                        'ask': 101
                    },
                    {
                        'strike': 151,
                        'bid': 300,
                        'ask': 301
                    }
                ]
            }
        ]

    def getContractFromDateChain(self, strike, chain):
        return min(chain, key=lambda x: abs(x['strike'] - strike))
