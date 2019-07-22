import numpy as np
import time
import random
import sys

from AsciiDataFile.Writers import MDDataFileWriter, DataColumnWriter

lapse = 1

nb = 0
# data_file = MDDataFileWriter('Data/md_data_file{0:d}.txt'.format(nb),auto_numbering = False)
data_file = DataColumnWriter('Data/data_column_file{0:d}.txt'.format(nb),auto_numbering = False)
data_file.write_header(['index','time','voltage','petit voltage'],['#','sec','V','mV'])

lastX = 0.7
lastY = 0.7
t0 = time.time()
for i in range(100):
    new_data = [i*100,time.time() - t0,lastX,lastY]
    lastX += random.random()/40
    lastY += random.random()/40
    print(new_data)
    data_file.add_data_point(new_data)
    time.sleep(lapse)

# f.close()