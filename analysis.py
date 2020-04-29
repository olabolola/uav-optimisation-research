import matplotlib.pyplot as plt
import numpy as np


lines_random = open('results/result_random.txt', 'r').readlines()
lines_next_closest = open('results/result_next_closest.txt', 'r').readlines()

steps_random = []
steps_next_closest = []
for line in lines_random:
    steps_random.append(int(line.split('= ')[-1]))
for line in lines_next_closest:
    steps_next_closest.append(int(line.split('= ')[-1]))

# print(steps_random)
# print(steps_next_closest)

x = np.arange(20)
ax = plt.subplot(111)
ax.bar(x, steps_random, color='b', align='center', label='random', width=0.4)
ax.bar(x+0.4, steps_next_closest, color='r', align='center', label = 'next closest', width=0.4)
plt.xlabel('run number')
plt.ylabel('number of steps till done')
plt.legend()
# plt.bar(range(len(steps_random)), steps_random)
plt.show()