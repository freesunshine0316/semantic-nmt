import sys
import matplotlib.pyplot as plt

name = ''
lst = []
for line in sys.stdin:
    line = line.strip().split()
    if line[0] != name:
        if len(lst) > 0:
            plt.plot(lst)
        name = line[0]
        lst = []
    lst.append(float(line[3]))
if len(lst) > 0:
   plt.plot(lst)
plt.show()

