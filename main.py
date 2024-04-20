import timeit
import random
import os
from typing import Tuple, Dict, List
import warnings
import tqdm
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


# This is the directory where our saved states are saved
saved_states_dir: str = "saved_states"


no_customers_values = (50, 100, 200, 400)

file_utils.initialise_results_file_with_columns(results_file_path="results/results.csv")

start = timeit.default_timer()

drone_capacity_values: Tuple[int, ...] = (
    1,
    2,
    3,
)

no_drones_values: Tuple[int, ...] = (1, 2, 3, 4)

strategies: Tuple[str, str, str, str] = (
    "farthest_package_first_MPA",
    "farthest_package_first",
    "closest_package_first",
    "most_packages_first",
)

NUMBER_OF_ITERATIONS: int = 10

no_clusters_per_no_customers: Dict[int, List[int]] = {
    50: [2],
    100: [2, 4],
    200: [2, 4, 8],
    400: [2, 4, 8, 16],
}

# no_clusters_per_no_customers: Dict[int, List[int]] = {
#     50: [2],
#     100: [2, 4],
#     200: [2, 4],
#     400: [2, 4],
# }

TOTAL_NO_ITERATIONS: int = (
    sum(
        len(no_clusters_per_no_customers[no_customers])
        for no_customers in no_customers_values
    )
    * NUMBER_OF_ITERATIONS
    * len(no_drones_values)
    * len(strategies)
    * len(drone_capacity_values)
)


progress_bar = tqdm.tqdm(total=TOTAL_NO_ITERATIONS, desc="Progress", unit="iteration")


for strategy in strategies:
    logger.info("Strategy: %s", strategy)
    for drone_capacity in drone_capacity_values:
        for no_customers in no_customers_values:
            for no_clusters in no_clusters_per_no_customers[no_customers]:
                for no_drones in no_drones_values:
                    for i in range(NUMBER_OF_ITERATIONS):

                        debug_string: str = (
                            f"No Drones: {no_drones}, drone cap: {drone_capacity}, no cust: {no_customers}, no_clusters: {no_clusters}, Iteration: {i}"
                        )
                        # logger.debug(debug_string)
                        progress_bar.update(1)
                        progress_bar.set_description(f"Progress - {debug_string}")

                        filename = os.path.join(
                            saved_states_dir, f"saved_state_{no_customers}_{i}.csv"
                        )

                        params = {
                            "load_file": filename,
                            "strategy": strategy,
                            "drone_capacity": drone_capacity,
                        }

                        results = EnvRunner.run_env(
                            load_file=params["load_file"],
                            no_drones=no_drones,
                            load=True,
                            no_clusters=no_clusters,
                            strategy=params["strategy"],
                            drone_capacity=params["drone_capacity"],
                        )

                        spans: Dict[int, int] = results["spans"]
                        no_dropoffs: Dict[int, int] = results["no_dropoffs"]

                        # Here we store the number of packages for each group of no_packages.
                        no_packages_total = file_utils.get_total_no_packages(filename)
                        no_packages_per_category = (
                            file_utils.get_no_packages_per_category(
                                filename, list(spans.keys())
                            )
                        )
                        no_customers_per_no_packages = (
                            file_utils.get_no_customers_per_no_packages(
                                filename, list(spans.keys())
                            )
                        )
                        # This is to prevent division by 0 errors
                        if no_packages_per_category[2] == 0:
                            avg_span_2: float = -1.0
                            avg_nodropoofs_2: float = -1.0
                        else:
                            avg_span_2 = round(
                                spans[2] / no_customers_per_no_packages[2], 2
                            )
                            avg_nodropoofs_2 = round(
                                no_dropoffs[2] / no_packages_per_category[2], 2
                            )
                        if no_packages_per_category[3] == 0:
                            avg_span_3: float = -1.0
                            avg_nodropoofs_3: float = -1.0
                        else:
                            avg_span_3 = round(
                                spans[3] / no_customers_per_no_packages[3], 2
                            )
                            avg_nodropoofs_3 = round(
                                no_dropoffs[3] / no_packages_per_category[3], 2
                            )
                        if no_packages_per_category[4] == 0:
                            avg_span_4: float = -1.0
                            avg_nodropoofs_4: float = -1.0
                        else:
                            avg_span_4 = round(
                                spans[4] / no_customers_per_no_packages[4], 2
                            )
                            avg_nodropoofs_4 = round(
                                no_dropoffs[4] / no_packages_per_category[4], 2
                            )

                            file_utils.save_result(
                                scenario_id=i,
                                strategy=strategy,
                                results={
                                    "steps": results["steps"],
                                    "drone_travel_distance": round(
                                        results["drone_travel_distance"], 2
                                    ),
                                    "truck_travel_distance": round(
                                        results["truck_travel_distance"], 2
                                    ),
                                    "X1": results["X1"],
                                    "X2": results["X2"],
                                    "utilization": round(results["utilization"], 2),
                                    "total_package_waiting_time": results[
                                        "total_package_waiting_time"
                                    ],
                                    "total_customer_waiting_time": results[
                                        "total_customer_waiting_time"
                                    ],
                                    "total_delay_time": results["total_delay_time"],
                                    "avg_span_2": avg_span_2,
                                    "avg_span_3": avg_span_3,
                                    "avg_span_4": avg_span_4,
                                    "avg_nodropoofs_2": avg_nodropoofs_2,
                                    "avg_nodropoofs_3": avg_nodropoofs_3,
                                    "avg_nodropoofs_4": avg_nodropoofs_4,
                                    "no_preventions": results["no_preventions"],
                                    "no_battery_swaps": results["no_battery_swaps"],
                                    "no_clusters": no_clusters,
                                },
                                information={
                                    "no_drones": no_drones,
                                    "drone_capacity": drone_capacity,
                                    "no_customers": no_customers,
                                    "no_packages_total": no_packages_total,
                                },
                            )

stop = timeit.default_timer()

logger.info("Time to complete simulation: %f", stop - start)
