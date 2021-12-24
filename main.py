from cc import writeCcs
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api

starttime = time.time()

api = Api(apiKey, apiRedirectUri)

while True:
    api.connect()
    # todo notify if fails and needs manual input

    canExecute = debugMarketOpen or api.optionExecutionWindowOpen()

    if canExecute:
        # todo cache execution date from api and sleep until that date & time
        writeCcs(api)
    else:
        print('Waiting for last market hour ...')

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
