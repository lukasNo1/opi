from cc import writeCcs, writeCc
import time

starttime = time.time()

while True:
    writeCcs()

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
