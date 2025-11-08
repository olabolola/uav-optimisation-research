import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


# Setting font parameters
font = {"family": "normal", "weight": "bold", "size": 12}

plt.rc("font", **font)


colors = ["#727272", "#f1595f", "#79c36a", "#599ad3"]
no_customer_values = (50, 100, 200, 500)
drone_capacity_values = (1, 2, 3, 4)


def get_average_no_dropoffs_per_strategy(df, save=False):
    mean_values = {}

    mean_values["Average nodropoffs 2"] = []
    mean_values["Average nodropoffs 3"] = []
    mean_values["Average nodropoffs 4"] = []

    for strategy in strategies:
        mean_values["Average nodropoffs 2"].append(
            df[df.strategy == strategy]["avg_nodropoffs_2"].mean()
        )
        mean_values["Average nodropoffs 3"].append(
            df[df.strategy == strategy]["avg_nodropoffs_3"].mean()
        )
        mean_values["Average nodropoffs 4"].append(
            df[df.strategy == strategy]["avg_nodropoffs_4"].mean()
        )

    df_plot = pd.DataFrame(mean_values, index=strategies)
    df_plot.plot(kind="bar", rot=0, color=colors)

    plt.legend(loc="lower right")
    plt.xlabel("Strategies")
    plt.ylabel("Average number of dropoffs")
    if save:
        path = "figures/"
        filename = f"Average number of dropoffs for every strategy"
        plt.savefig(path + filename)
        plt.close()
    else:
        plt.show()


def get_average_spans_per_strategy(df, save=False):
    mean_values = {}

    mean_values["Average span 2"] = []
    mean_values["Average span 3"] = []
    mean_values["Average span 4"] = []

    for strategy in strategies:
        mean_values["Average span 2"].append(
            df[df.strategy == strategy]["avg_span_2"].mean()
        )
        mean_values["Average span 3"].append(
            df[df.strategy == strategy]["avg_span_3"].mean()
        )
        mean_values["Average span 4"].append(
            df[df.strategy == strategy]["avg_span_4"].mean()
        )

    df_plot = pd.DataFrame(mean_values, index=strategies)
    df_plot.plot(kind="bar", rot=0, color=colors)

    plt.xlabel("Strategies")
    plt.ylabel("Average spans")
    if save:
        path = "figures/"
        filename = f"Average spans for every strategy"
        plt.savefig(path + filename)
        plt.close()
    else:
        plt.show()


df = pd.read_csv("results/results - wait for capacity.csv")

df.strategy = df.strategy.replace("farthest_package_first", "FPF")
df.strategy = df.strategy.replace("closest_package_first", "CPF")
df.strategy = df.strategy.replace("most_packages_first", "MPF")
df.strategy = df.strategy.replace("farthest_package_first_MPA", "FPF_MPA")
cols = [
    "total_time",
    "package_delivery_time",
    "drone_travel_distance",
    "utilization",
    "avg_package_wait_time",
    "avg_customer_wait_time",
    "total_delay_time",
    "avg_span_2",
    "avg_span_3",
    "avg_span_4",
    "avg_nodropoffs_2",
    "avg_nodropoffs_3",
    "avg_nodropoffs_4",
    "no_preventions",
]
# bies = ['drone_capacity', 'no_customers']
df.avg_span_2 = df.avg_span_2.replace([-10], np.nan)
df.avg_span_3 = df.avg_span_3.replace([-10], np.nan)
df.avg_span_4 = df.avg_span_4.replace([-10], np.nan)
df.avg_nodropoffs_2 = df.avg_nodropoffs_2.replace([-10], np.nan)
df.avg_nodropoffs_3 = df.avg_nodropoffs_3.replace([-10], np.nan)
df.avg_nodropoffs_4 = df.avg_nodropoffs_4.replace([-10], np.nan)


strategies = ["FPF", "FPF_MPA", "CPF", "MPF"]

# for col in cols:
#     plot_by_X(df, col, save=True)

# for col in cols:
#     for by in ('no_customers', 'drone_capacity'):
#         plot_by_X2(df, col, by = by, save=True)

# get_average_spans_per_strategy(df, save=True)
# get_average_no_dropoffs_per_strategy(df, save=True)
# print(df.head())
