import sys
from datetime import datetime


def generateLog(fileName: str = None):
    start = datetime.now()
    if fileName:
        logfile = f"{fileName}.log"
    else:
        logfile = "log.log"
    print("Saving Log to: " + logfile)
    sys.stdout = open(logfile, "w")
    print("Log Start time: " + str(start) + "\n")
    return start
