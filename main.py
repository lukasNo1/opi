from cc import writeCcs, writeCc
import time
from configuration import apiKey, apiRedirectUri
from api import Api

starttime = time.time()

api = Api(apiKey, apiRedirectUri)


while True:
    api.connect()
    # todo maybe outside of loop & reconnect function

    marketOpen = api.isEquityRegularMarketOpen()

    if marketOpen:
        writeCcs(api)
    else:
        print('Nothing to write ...')

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
