import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


df = pd.read_csv('results/results.txt')

# print(df.X1.min())
# print(df.X2.min())
# print(df.utilization.mean())

# x = df[(df.no_customers == 500) & (df.drone_capacity == 2)]

# x1 = x[x.strategy == 'farthest_package_first'].X2.mean()
# x2 = x[x.strategy == 'closest_package_first'].X2.mean()
# x3 = x[x.strategy == 'most_packages_first'].X2.mean()
# x4 = x[x.strategy == 'farthest_package_first_MPA'].X2.mean()


# vals = [x1, x2, x3, x4]

# x_axis = np.arange(4)
# x_ticks = ['FPF', 'CPF', 'MPF', 'FPF_MPA']


# plt.bar(x_axis, vals, color = ['r', 'g', 'b', '#654987'])

# plt.xticks(x_axis, x_ticks)

# plt.show()