import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


x1, y1 = np.loadtxt('averagewaitingtime1(packet_size_change).out', delimiter='\t', unpack=True)
x1=x1/1000
y1=1000*y1
plt.plot(x1, y1, 'rx')


# add labels, legend, and title
#plt.xlabel(r'bucket size $\lambda$ [pkts/s]')
plt.xlabel(r'packet size [E+3Byte]')
plt.ylabel(r'average delay [E-03s]')
plt.legend()
#plt.title(r'average delay for different bucket size ($\mu=100$ [pkts/s])')
plt.title(r'Average delay for different packet size')
plt.savefig('average_delay(time change).pdf')
plt.axis([0,10,0,5])
plt.show()


