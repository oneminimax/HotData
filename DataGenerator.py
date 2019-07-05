import numpy as np
import time
import random
import sys

sys.path.append("/Users/oneminimax/Documents/Projets Programmation")

from AsciiDataFile.Writers import MDDataFileWriter as Writer

lapse = 0.66

nb = 0
dataFile = Writer('Data/workfile{0:d}.txt'.format(nb),auto_numbering = False)
dataFile.write_header(['index','time','voltage','petit voltage'],['#','sec','V','mV'])

lastX = 0
lastY = 0
t0 = time.time()
for i in range(100):
    newData = [i*100,time.time() - t0,lastX,lastY]
    lastX += (random.random()-0.5)/10
    lastY += (random.random()-0.5)/10
    print(newData)
    dataFile.add_data_point(newData)
    time.sleep(lapse)

# f.close()