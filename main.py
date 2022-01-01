from cc import writeCcs
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api
import datetime

api = Api(apiKey, apiRedirectUri)

defaultWaitTime = 3600

while True:
    api.connect()

    execWindow = api.getOptionExecutionWindow()

    if debugMarketOpen or execWindow['open']:
        print('Market open, running the program now ...')
        writeCcs(api)

        time.sleep(defaultWaitTime)
    else:
        if execWindow['openDate']:
            print('Waiting for last market hour ...')

            delta = execWindow['openDate'] - execWindow['nowDate']

            if delta > datetime.timedelta(0):
                print('Window open in: %s. waiting ...' % delta)
                time.sleep(delta.total_seconds())
            else:
                # we are past open date, but the market is not open
                print('Market closed already. Rechecking in 1 hour ...')
                time.sleep(defaultWaitTime)

        else:
            print('The market is closed today, rechecking in 1 hour ...')
            time.sleep(defaultWaitTime)
