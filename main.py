from cc import writeCcs
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api
import datetime

api = Api(apiKey, apiRedirectUri)

while True:
    api.connect()

    execWindow = api.getOptionExecutionWindow()

    if debugMarketOpen or execWindow['open']:
        writeCcs(api)
    else:
        print('Waiting for last market hour ...')

        if execWindow['openDate']:
            delta = execWindow['openDate'] - execWindow['nowDate']

            if delta > datetime.timedelta(0):
                print('Window open in: %s. waiting ...' % delta)
                time.sleep(delta.total_seconds())
            else:
                # we are past open date, but the market is not open
                print('Market closed. Rechecking in 1 hour ...')
                time.sleep(3600)

        else:
            print('Cant get the market open date, retrying in 1 min ...')
            time.sleep(60.0)
