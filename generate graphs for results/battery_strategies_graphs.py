import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


colors = ["#727272", "#599ad3"]
no_customer_values = (50, 100, 200, 500)
drone_capacity_values = (1, 2, 3)


def get_battery_strategy_vs_noc_and_dc(mean_value_col, by: str, save=False):
    mean_values = {}

    mean_values["launch immediately"] = []
    mean_values["wait for capacity"] = []

    if by == "no_customers":
        for no_customers in no_customer_values:
            mean_values["launch immediately"].append(
                df[(df.no_customers == no_customers) & (df.strategy == "FPF_MPA")][
                    mean_value_col
                ].mean()
            )

    elif by == "drone_capacity":
        for drone_capacity in drone_capacity_values:
            mean_values["launch immediately"].append(
                df[(df.drone_capacity == drone_capacity) & (df.strategy == "FPF_MPA")][
                    mean_value_col
                ].mean()
            )

    if by == "no_customers":
        df_plot = pd.DataFrame(mean_values, index=no_customer_values)
    elif by == "drone_capacity":
        df_plot = pd.DataFrame(mean_values, index=drone_capacity_values)
    df_plot.plot(kind="bar", rot=0, color=colors)
    plt.ylabel(mean_value_col)
    plt.xlabel(by)
    plt.legend(loc="lower right")
    if save:
        path = "figures/"
        filename = f"{by} vs {mean_value_col} for each strategy"
        plt.savefig(path + filename)
    else:
        plt.show()


df = pd.read_csv("../results/results.csv")

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


for col in cols:
    for by in ("no_customers", "drone_capacity"):
        get_battery_strategy_vs_noc_and_dc(col, by=by, save=False)

get_battery_strategy_vs_noc_and_dc("total_time", "drone_capacity", save=False)
