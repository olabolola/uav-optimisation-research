import timeit
import random
from typing import Tuple, Dict
import warnings

from gymnasium.envs.registration import register

from logger_setup import logger
import file_utils
from env_runner import EnvRunner

random.seed(42)

register(
    id="HDS-v1",
    entry_point="UAV_RL_env.envs:custom_class",
)

warnings.filterwarnings("ignore", category=UserWarning)

# I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs
# scenarios with the 'random' strategy and compare the number of steps
p = [0.85, 0.09, 0.04, 0.02]

# This is the directory where our saved states are saved
saved_states_path: str = "../saved_states/"

# This is just for testing
# drone_capacity = 1
# filename = path + 'saved_state_200_0.txt'
# strategy = 'farthest_package_first_MPA'
# EnvRunner.run_env(6, no_trucks, None, no_drones, None, p, load=True, load_file = filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)

# Generate the 40 test files

no_customers_values = (50, 100, 200, 500)
# strategy = 'farthest_package_first'

# for no_customers in no_customers_values:

#     for i in range(10):
#         EnvRunner.run_env(i, no_trucks, 2, no_drones, no_customers, p, load=False, load_file=None, strategy=strategy, save_state=True, drone_capacity = 10)


file_utils.initialise_results_file_with_columns(results_file_path="results/results.csv")

start = timeit.default_timer()

drone_capacity_values: Tuple[int, ...] = (
    1,
    2,
    3,
)  # We will be testing these values of drone_capacity in our simulation

strategies: Tuple[str, str, str, str] = (
    "farthest_package_first_MPA",
    "farthest_package_first",
    "closest_package_first",
    "most_packages_first",
)

NUMBER_OF_ITERATIONS: int = 1


for strategy in strategies:
    logger.info("Strategy: %s", strategy)
    for drone_capacity in drone_capacity_values:
        for no_customers in no_customers_values:
            for i in range(NUMBER_OF_ITERATIONS):

                logger.debug(
                    "Drone Capacity: %d, Number of customers: %d, Iteration: %d",
                    drone_capacity,
                    no_customers,
                    i,
                )

                filename: str = f"{saved_states_path}saved_state_{no_customers}_{i}.txt"

                params = {
                    "load_file": filename,
                    "strategy": strategy,
                    "drone_capacity": drone_capacity,
                }
                results = EnvRunner.run_env(
                    load_file=params["load_file"],
                    load=True,
                    strategy=params["strategy"],
                    drone_capacity=params["drone_capacity"],
                    # p=p,
                )

                spans: Dict[int, int] = results["spans"]
                no_dropoffs: Dict[int, int] = results["no_dropoffs"]

                # Here we store the number of packages for each group of no_packages.
                no_packages_total = file_utils.get_total_no_packages(filename)
                no_packages_per_category = file_utils.get_no_packages_per_category(
                    filename, list(spans.keys())
                )
                no_customers_per_no_packages = (
                    file_utils.get_no_customers_per_no_packages(
                        filename, list(spans.keys())
                    )
                )
                # This is to prevent division by 0 errors
                if no_packages_per_category[2] == 0:
                    avg_span_2 = -10
                    avg_nodropoofs_2 = -10
                else:
                    avg_span_2 = round(spans[2] / no_customers_per_no_packages[2], 2)
                    avg_nodropoofs_2 = round(
                        no_dropoffs[2] / no_packages_per_category[2], 2
                    )
                    # avg_nodropoofs_2 = round(no_dropoffs[2] / no_customers_per_no_packages[2], 2)
                if no_packages_per_category[3] == 0:
                    avg_span_3 = -10
                    avg_nodropoofs_3 = -10
                else:
                    avg_span_3 = round(spans[3] / no_customers_per_no_packages[3], 2)
                    avg_nodropoofs_3 = round(
                        no_dropoffs[3] / no_packages_per_category[3], 2
                    )
                    # avg_nodropoofs_3 = round(no_dropoffs[3] / no_customers_per_no_packages[3], 2)
                if no_packages_per_category[4] == 0:
                    avg_span_4 = -10
                    avg_nodropoofs_4 = -10
                else:
                    avg_span_4 = round(spans[4] / no_customers_per_no_packages[4], 2)
                    avg_nodropoofs_4 = round(
                        no_dropoffs[4] / no_packages_per_category[4], 2
                    )
                    # avg_nodropoofs_4 = round(no_dropoffs[4] / no_customers_per_no_packages[4], 2)
                file_utils.save_result(
                    i,
                    strategy,
                    (
                        results["steps"][0],
                        results["steps"][1],
                        round(results["drone_travel_distance"], 2),
                        round(results["truck_travel_distance"], 2),
                        results["X1"],
                        results["X2"],
                        round(results["utilization"], 2),
                        round(
                            results["total_package_waiting_time"] / no_packages_total, 2
                        ),
                        round(results["total_customer_waiting_time"] / no_customers, 2),
                        results["total_delay_time"],
                        avg_span_2,
                        avg_span_3,
                        avg_span_4,
                        avg_nodropoofs_2,
                        avg_nodropoofs_3,
                        avg_nodropoofs_4,
                        results["no_preventions"],
                    ),
                    (drone_capacity, no_customers),
                )


stop = timeit.default_timer()

logger.info("Time to complete simulation: %f", stop - start)
