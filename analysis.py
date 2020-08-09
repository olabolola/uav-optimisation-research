import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

strategies = ['FPF', 'CPF', 'MPF', 'FPF_MPA']
color = ['r', 'g', 'b', 'y']


df = pd.read_csv('results/results.txt')
x = df[['strategy', 'drone_capacity', 'total_time']]

x.strategy = x.strategy.replace('farthest_package_first', 'FPF')
x.strategy = x.strategy.replace('closest_package_first', 'CPF')
x.strategy = x.strategy.replace('most_packages_first', 'MPF')
x.strategy = x.strategy.replace('farthest_package_first_MPA', 'FPF_MPA')


x.groupby(['strategy', 'total_time']).total_time.mean().plot(x='strategy', kind='bar', rot=0, color=color)
plt.show()