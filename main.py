from cc import writeCcs
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api
import datetime

starttime = time.time()

api = Api(apiKey, apiRedirectUri)

while True:
    api.connect()

    execWindow = debugMarketOpen or api.getOptionExecutionWindow()

    if execWindow['open']:
        writeCcs(api)
    else:
        print('Waiting for last market hour ...')

        if execWindow['openDate']:
            delta = execWindow['openDate'] - execWindow['nowDate']

            if delta > datetime.timedelta(0):
                print('Window open in: %s. waiting ...' % delta)
                time.sleep(delta.total_seconds())
            else:
                # we are past open date, but the api says market is not open

                delta = 3600

                print('Market closed. Rechecking in 1 hour ...')
                time.sleep(delta)

        else:
            print('Cant get the market open date, retrying in 1 min ...')
            time.sleep(60.0 - ((time.time() - starttime) % 60.0))
