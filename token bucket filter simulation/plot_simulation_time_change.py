import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)


x1, y1 = np.loadtxt('change_simulation_time.txt', delimiter='\t', unpack=True)
x1=x1*1000
y1=100000*y1
#m1=[0.002,0.004,0.006,0.008,0.01,0.012,0.014,0.016,0.018,0.02,0.022,0.024,0.026,0.028,0.03,0.032,0.034,0.036,0.038,0.04,0.042,0.044]
#m2=[1.00E-05,1.90E-05,3.23E-05,3.90E-05,5.00E-05,7.46E-05,1.12E-04,1.52E-04,2.04E-04,2.73E-04,3.39E-04,4.10E-04,4.84E-04,5.61E-04,6.40E-04,7.21E-04,8.04E-04,8.82E-04,9.52E-04,1.02E-03,1.07E-03,1.13E-03]
#m1=1000*m1
#m2=1000*m2
#plt.plot(x2, y2, 'rx', label="Simulation")
plt.plot(x1, y1, 'rx')


# add labels, legend, and title
#plt.xlabel(r'bucket size $\lambda$ [pkts/s]')
plt.xlabel(r'simulation time [E-3Byte]')
plt.ylabel(r'average delay [E-05s]')
plt.legend()
#plt.title(r'average delay for different bucket size ($\mu=100$ [pkts/s])')
plt.title(r'Average delay for different simulation time')
plt.savefig('average_delay(time change).pdf')
plt.axis([0,45,0,100])
plt.show()


