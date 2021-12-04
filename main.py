from cc import writeCcs, writeCc
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api

starttime = time.time()

api = Api(apiKey, apiRedirectUri)

while True:
    api.connect()
    # todo notify if fails and needs manual input

    marketOpen = debugMarketOpen or api.isOptionMarketOpen()

    if marketOpen:
        writeCcs(api)
    else:
        print('Market closed. Nothing to write ...')

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
