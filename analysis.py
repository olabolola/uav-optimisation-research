import matplotlib.pyplot as plt



lines = open('results/result.txt', 'r').readlines()

steps = []
for line in lines:
    steps.append(int(line.split('= ')[-1]))
print(steps)

plt.hist(steps)
plt.show()