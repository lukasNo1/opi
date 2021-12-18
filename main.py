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
        # todo break when nothing to write, then sleep for 24 hours from execution start date
        writeCcs(api)
    else:
        print('Waiting for option execution window to open ...')

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
