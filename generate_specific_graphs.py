import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

colors = ['#727272', '#f1595f', '#79c36a', '#599ad3']

def plot_by_X(df, mean_value_col, save = False):
    mean_values = []

    for strategy in strategies:
        mean_values.append(df[df.strategy == strategy][mean_value_col].mean())
    plt.bar(strategies, mean_values, color = colors)
    # print(mean_values)
    # plt.show()
    # df_plot = pd.DataFrame(mean_values)
    # df_plot.index = strategies
    
    # df_plot.plot(kind='bar', rot=0)
    
    plt.ylabel(mean_value_col)
    if save:
        path = 'figures/strategy_impact/'
        filename = f'{mean_value_col} for each strategy'
        plt.savefig(path + filename)
        plt.close()
    else:
        plt.show()
    




df = pd.read_csv('results/results.csv')

df.strategy = df.strategy.replace('farthest_package_first', 'FPF')
df.strategy = df.strategy.replace('closest_package_first', 'CPF')
df.strategy = df.strategy.replace('most_packages_first', 'MPF')
df.strategy = df.strategy.replace('farthest_package_first_MPA', 'FPF_MPA')
cols = ['total_time', 'package_delivery_time', 'drone_travel_distance', 'utilization', 'avg_package_wait_time', 'avg_customer_wait_time', 'total_delay_time', 'avg_span_2', 'avg_span_3', 'avg_span_4', 'avg_nodropoffs_2', 'avg_nodropoffs_3', 'avg_nodropoffs_4', 'no_preventions_first', 'no_preventions_total']
# bies = ['drone_capacity', 'no_customers']
df.avg_span_2 = df.avg_span_2.replace([-10], np.nan)
df.avg_span_3 = df.avg_span_3.replace([-10], np.nan)
df.avg_span_4 = df.avg_span_4.replace([-10], np.nan)
df.avg_nodropoffs_2 = df.avg_nodropoffs_2.replace([-10], np.nan)
df.avg_nodropoffs_3 = df.avg_nodropoffs_3.replace([-10], np.nan)
df.avg_nodropoffs_4 = df.avg_nodropoffs_4.replace([-10], np.nan)

no_customer_values = (50, 100, 200, 500)
drone_capacity_values = (1, 2, 3, 4)
strategies = ['FPF', 'FPF_MPA', 'CPF', 'MPF']

for col in cols:
    plot_by_X(df, col, save=True)

# plot_by_X(df, 'drone_capacity', 'avg_span_2', save=False)
