from cc import writeCcs, writeCc
import time

starttime = time.time()

# writeCc('QQQ',{'contract':'QQQ123'})

while True:
    writeCcs()

    time.sleep(60.0 - ((time.time() - starttime) % 60.0))

