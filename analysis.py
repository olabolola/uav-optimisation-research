import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

no_customer_values = (50, 100, 200, 500)
drone_capacity_values = (1, 2, 3)
strategies = ['FPF', 'CPF', 'MPF', 'FPF_MPA']

def plot_by_X(df, by, mean_value_col, save = False):
    mean_values = {}

    for strategy in strategies:
        mean_values[strategy] = []

    for strategy in mean_values.keys():
        if by == 'no_customers':
            for no_customers in no_customer_values:
                mean_values[strategy].append(df[(df.no_customers == no_customers) & (df.strategy == strategy)][mean_value_col].mean())
        elif by == 'drone_capacity':
            for drone_capacity in drone_capacity_values:
                mean_values[strategy].append(df[(df.drone_capacity == drone_capacity) & (df.strategy == strategy)][mean_value_col].mean())

    if by == 'no_customers':
        df_plot = pd.DataFrame(mean_values, index = no_customer_values)
    elif by == 'drone_capacity':
        df_plot = pd.DataFrame(mean_values, index = drone_capacity_values)
        
    # # print(mean_values)
    # # print(df_plot)
    df_plot.plot(kind='bar', rot=0)
    plt.ylabel(mean_value_col)
    plt.xlabel(by)
    if save:
        path = 'figures/'
        filename = f'{by} vs {mean_value_col} for each strategy'
        plt.savefig(path + filename)
    else:
        plt.show()
    

color = ['r', 'g', 'b', 'y']


df = pd.read_csv('results/results.csv')

df.strategy = df.strategy.replace('farthest_package_first', 'FPF')
df.strategy = df.strategy.replace('closest_package_first', 'CPF')
df.strategy = df.strategy.replace('most_packages_first', 'MPF')
df.strategy = df.strategy.replace('farthest_package_first_MPA', 'FPF_MPA')

cols = ['total_time', 'A', 'drone_travel_distance', 'utilization', 'avg_package_wait_time', 'avg_customer_wait_time', 'total_delay_time', 'avg_span_2', 'avg_span_3', 'avg_span_4', 'avg_nodropoffs_2', 'avg_nodropoffs_3', 'avg_nodropoffs_4']
bies = ['drone_capacity', 'no_customers']

df.avg_span_2 = df.avg_span_2.replace([-10], np.nan)
df.avg_span_3 = df.avg_span_3.replace([-10], np.nan)
df.avg_span_4 = df.avg_span_4.replace([-10], np.nan)
df.avg_nodropoffs_2 = df.avg_nodropoffs_2.replace([-10], np.nan)
df.avg_nodropoffs_3 = df.avg_nodropoffs_3.replace([-10], np.nan)
df.avg_nodropoffs_4 = df.avg_nodropoffs_4.replace([-10], np.nan)

for by in bies:
    for col in cols:
        plot_by_X(df, by, col, save=True)

# print(df[(df.drone_capacity == 2) & (df.strategy == 'MPF')].avg_span_2.mean())

# path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'
# no_packages_per_category = {i:0 for i in range(2, 5)}
# for no_customers in no_customer_values:
#     for drone_capacity in drone_capacity_values:
#         for i in range(10):
#             filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
#             f = open(filename).readlines()
#             for line in f[1:]:
#                 no_packages = int(line.split(',')[-1])
#                 if no_packages > 1:
#                     no_packages_per_category[no_packages] += no_packages

# print(no_packages_per_category)