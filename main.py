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
        rollDate1Am = support.getDeltaDiffNowNextRollDate1Am()
        tomorrow1Am = support.getDeltaDiffNowTomorrow1Am()

        if rollDate1Am is not None and tomorrow1Am < rollDate1Am:
            # we don't need to do anything, but we are making a call every day to make sure the refresh token stays valid
            waitTime = support.getDeltaDiffNowTomorrow1Am()

            print('Token refreshed, waiting for roll date in %s' % rollDate1Am)

            time.sleep(waitTime.total_seconds())
        else:
            if debugMarketOpen or execWindow['open']:
                print('Market open, running the program now ...')
                writeCcs(api)

                nextRollDate = support.getDeltaDiffNowNextRollDate1Am()

                print('All done. The next roll date is in %s' % nextRollDate)

                # we are making a call every day to make sure the refresh token stays valid
                waitTime = support.getDeltaDiffNowTomorrow1Am()

                time.sleep(waitTime.total_seconds())
            else:
                if execWindow['openDate']:
                    print('Waiting for execution window to open ...')

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
