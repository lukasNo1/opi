from cc import writeCcs
import time
from configuration import apiKey, apiRedirectUri, debugMarketOpen
from api import Api
import datetime
import alert
import support

api = Api(apiKey, apiRedirectUri)

try:
    while True:
        api.connect()

        execWindow = api.getOptionExecutionWindow()

        if debugMarketOpen or execWindow['open']:
            print('Market open, running the program now ...')
            writeCcs(api)

            # gets diff to nearest expiration date -1, fallback to defaultWaitTime
            waitTime = support.getDeltaDiffNowNearestExpirationDate()

            print('All done. Running again in %s' % waitTime)

            time.sleep(waitTime.total_seconds())
        else:
            if execWindow['openDate']:
                print('Waiting for last market hour ...')

                delta = execWindow['openDate'] - execWindow['nowDate']

                if delta > datetime.timedelta(0):
                    print('Window open in: %s. waiting ...' % delta)
                    time.sleep(delta.total_seconds())
                else:
                    # we are past open date, but the market is not open
                    waitTime = support.getDeltaDiffNowTomorrow1Am()

                    print('Market closed already. Rechecking tomorrow (in %s)' % waitTime)

                    time.sleep(waitTime.total_seconds())

            else:
                print('The market is closed today, rechecking in 1 hour ...')
                time.sleep(support.defaultWaitTime)
except Exception as e:
    alert.botFailed(None, 'Uncaught exception: ' + str(e))
