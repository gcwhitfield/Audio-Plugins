from concurrent.futures import ProcessPoolExecutor
import scipy.signal
import numpy as np
from matplotlib import pyplot as plt
import math

# derivation of pole and zero locations for phaser taken from 
# https://ccrma.stanford.edu/~jos/pasp/Phasing_2nd_Order_Allpass_Filters.html
for x in range(1, 6):
    angle = math.pi * 0.5
    R = 0.5
    a2 = R * R
    a1 = -2 * R * math.cos(angle)
    x = x * 0.05
    #pole = np.array([x, x])
    #root = np.array([1/x, 1/x])
    b = np.array([a2, a1, 1])
    a = np.array([1, a1, a2])
    w, h = scipy.signal.freqz(b, a)
    plt.plot(w, np.angle(h))
    plt.xlabel("Frequency (radian)")
    plt.ylabel("Phase shift, x = " + str(x))
    plt.show()