import numpy as np
import time

lapse = 1

f = open('workfile.txt', 'w')

for i in range(100):
    string = "{0:d} ligne sont ecrites\n".format(i)
    print(string.strip())
    f.write(string)
    f.flush()
    time.sleep(lapse)

f.close()