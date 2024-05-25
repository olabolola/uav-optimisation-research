import timeit
import multiprocessing
import random
import statistics
import os
from typing import Tuple, Dict, List
import warnings
from gymnasium.envs.registration import register
import tqdm
from UAV_RL_env.envs.celes import Strategy

from logger_setup import logger
import file_utils
from env_runner import EnvRunner

random.seed(42)

register(
    id="HDS-v1",
    entry_point="UAV_RL_env.envs:custom_class",
)

warnings.filterwarnings("ignore", category=UserWarning)

saved_states_dir: str = "saved_states"

file_utils.initialise_results_file_with_columns(results_file_path="results/results.csv")

no_customers_values: Tuple[int, ...] = (50, 100, 200, 400)
drone_capacity_values: Tuple[int, ...] = (1, 2, 3)
no_drones_values: Tuple[int, ...] = (1, 2, 3, 4)
strategies: Tuple[str, str, str, str] = (
    Strategy.FARTHEST_PACKAGE_FIRST_MPA.value,
    Strategy.FARTHEST_PACKAGE_FIRST.value,
    Strategy.CLOSEST_PACKAGE_FIRST.value,
    Strategy.MOST_PACKAGES_FIRST.value,
    # "farthest_package_first_MPA",
    # "farthest_package_first",
    # "closest_package_first",
    # "most_packages_first",
    # "random_package_first",
    # "longest_waiting_package_first",
    # "densest_package_first",
)

NUMBER_OF_ITERATIONS: int = 10
no_clusters_per_no_customers: Dict[int, List[int]] = {
    50: [2],
    100: [2, 4],
    200: [2, 4, 8],
    400: [2, 4, 8, 16],
}


def run_iteration(args):
    strategy, drone_capacity, no_customers, no_clusters, no_drones, i = args
    filename = os.path.join(saved_states_dir, f"saved_state_{no_customers}_{i}.csv")
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
    spans: Dict[int, List[int]] = results["spans"]
    no_dropoffs: Dict[int, List[int]] = results["no_dropoffs"]
    no_packages_total = file_utils.get_total_no_packages(filename)
    no_customers_per_no_packages: Dict[int, int] = (
        file_utils.get_no_customers_per_no_packages(filename, [1, 2, 3, 4])
    )

    process_id = multiprocessing.current_process()._identity[0]
    file_utils.save_result(
        process_id=process_id,
        scenario_id=i,
        strategy=strategy,
        results={
            "steps": results["steps"],
            "drone_travel_distance": round(results["drone_travel_distance"], 2),
            "truck_travel_distance": round(results["truck_travel_distance"], 2),
            "Trucks In-Cluster time": results["X1"],
            "Drones Active Time": results["X2"],
            "Drone Utilization": round(results["utilization"], 2),
            "Total Package Delivery Time": results["total_package_waiting_time"],
            "Total Customer Delivery Time": results["total_customer_waiting_time"],
            "average_customer_waiting_time": results["average_customer_waiting_time"],
            "average_package_waiting_time": results["average_package_waiting_time"],
            "median_package_waiting_time": results["median_package_waiting_time"],
            "median_customer_waiting_time": results["median_customer_waiting_time"],
            "avg_span_2": statistics.mean(spans[2]) if len(spans[2]) > 0 else -1.0,
            "avg_span_3": statistics.mean(spans[3]) if len(spans[3]) > 0 else -1.0,
            "avg_span_4": statistics.mean(spans[4]) if len(spans[4]) > 0 else -1.0,
            "avg_nodropoofs_2": (
                statistics.mean(no_dropoffs[2]) if len(no_dropoffs[2]) > 0 else -1.0
            ),
            "avg_nodropoofs_3": (
                statistics.mean(no_dropoffs[3]) if len(no_dropoffs[3]) > 0 else -1.0
            ),
            "avg_nodropoofs_4": (
                statistics.mean(no_dropoffs[4]) if len(no_dropoffs[4]) > 0 else -1.0
            ),
            "median_span_2": statistics.median(spans[2]) if len(spans[2]) > 0 else -1.0,
            "median_span_3": statistics.median(spans[3]) if len(spans[3]) > 0 else -1.0,
            "median_span_4": statistics.median(spans[4]) if len(spans[4]) > 0 else -1.0,
            "median_nodropoofs_2": (
                statistics.median(no_dropoffs[2]) if len(no_dropoffs[2]) > 0 else -1.0
            ),
            "median_nodropoofs_3": (
                statistics.median(no_dropoffs[3]) if len(no_dropoffs[3]) > 0 else -1.0
            ),
            "median_nodropoofs_4": (
                statistics.median(no_dropoffs[4]) if len(no_dropoffs[4]) > 0 else -1.0
            ),
            "no_preventions": results["no_preventions"],
            "no_battery_swaps": results["no_battery_swaps"],
            "no_clusters": no_clusters,
            "no_of_customers_with_1_package": no_customers_per_no_packages[1],
            "no_of_customers_with_2_package": no_customers_per_no_packages[2],
            "no_of_customers_with_3_package": no_customers_per_no_packages[3],
            "no_of_customers_with_4_package": no_customers_per_no_packages[4],
        },
        information={
            "no_drones": no_drones,
            "drone_capacity": drone_capacity,
            "no_customers": no_customers,
            "no_packages_total": no_packages_total,
        },
    )
    return 1


if __name__ == "__main__":
    start = timeit.default_timer()

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

    pool = multiprocessing.Pool()
    progress_bar = tqdm.tqdm(
        total=TOTAL_NO_ITERATIONS, desc="Progress", unit="iteration"
    )

    args_list = []
    for strategy in strategies:
        for drone_capacity in drone_capacity_values:
            for no_customers in no_customers_values:
                for no_clusters in no_clusters_per_no_customers[no_customers]:
                    for no_drones in no_drones_values:
                        for i in range(NUMBER_OF_ITERATIONS):
                            args_list.append(
                                (
                                    strategy,
                                    drone_capacity,
                                    no_customers,
                                    no_clusters,
                                    no_drones,
                                    i,
                                )
                            )

    for _ in pool.imap_unordered(run_iteration, args_list):
        progress_bar.update(1)

    pool.close()
    pool.join()

    stop = timeit.default_timer()

    logger.info("Time to complete simulation: %f", stop - start)
