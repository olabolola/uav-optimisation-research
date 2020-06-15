import numpy as np
import random
import matplotlib.pyplot as plt

a = np.arange(1, 6)
freq = [0, 0, 0, 0, 0]


for _ in range(20):
    x = np.random.choice(a, p = [0.1, 0.1, 0.1, 0.1, 0.6])
    freq[x - 1] += 1

    print(x)
    
x_axis = np.arange(5)
ax = plt.subplot(111)
ax.bar(x_axis, freq)
plt.show()