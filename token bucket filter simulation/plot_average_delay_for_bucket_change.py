import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)

x1, y1 = np.loadtxt('averagewaitingtime3(token_bucket_size_change).out', delimiter='\t', unpack=True)
x1=x1/1000
y1=10000*y1
#plt.plot(x2, y2, 'rx', label="Simulation")
plt.plot(x1, y1, 'rx')

# add labels, legend, and title

plt.xlabel(r'bucket size [E+3Byte]')
plt.ylabel(r'average delay [E-04s]')
plt.legend()

plt.title(r'Average delay for different bucket size')
plt.savefig('average_delay(token_bucket_size_change).pdf')
plt.axis([0,10,0,5])
plt.show()
