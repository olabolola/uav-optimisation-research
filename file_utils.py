from typing import List, Tuple, Dict, Any
import pandas as pd
import os

# Define the schema for the results DataFrame
RESULTS_SCHEMA: List[Dict[str, Any]] = [
    {"name": "strategy", "type": str},
    {"name": "scenario_id", "type": int},
    {"name": "no_drones", "type": int},
    {"name": "drone_capacity", "type": int},
    {"name": "no_customers", "type": int},
    {"name": "total_time", "type": int},
    {"name": "package_delivery_time", "type": int},
    {"name": "drone_travel_distance", "type": float},
    {"name": "truck_travel_distance", "type": float},
    {"name": "total_cluster_time", "type": int},
    {"name": "total_active_time", "type": int},
    {"name": "utilization", "type": float},
    {"name": "avg_package_wait_time", "type": float},
    {"name": "avg_customer_wait_time", "type": float},
    {"name": "total_delay_time", "type": int},
    {"name": "avg_span_2", "type": float},
    {"name": "avg_span_3", "type": float},
    {"name": "avg_span_4", "type": float},
    {"name": "avg_nodropoffs_2", "type": float},
    {"name": "avg_nodropoffs_3", "type": float},
    {"name": "avg_nodropoffs_4", "type": float},
    {"name": "no_preventions", "type": int},
    {"name": "no_battery_swaps", "type": int},
    {"name": "no_clusters", "type": int},
]


def get_no_packages_per_category(filename: str, keys: List[int]):
    no_packages_per_category = {no: 0 for no in keys}
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            no_packages = int(line.split(",")[-1])
            if no_packages > 1:
                no_packages_per_category[no_packages] += no_packages
    return no_packages_per_category


def get_no_customers_per_no_packages(filename: str, keys: List[int]):
    no_customers_per_no_packages = {no: 0 for no in keys}
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            no_packages = int(line.split(",")[-1])
            if no_packages > 1:
                no_customers_per_no_packages[no_packages] += 1
    return no_customers_per_no_packages


def get_total_no_packages(filename: str):
    total_no_packages = 0
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            no_packages = int(line.split(",")[-1])
            total_no_packages += no_packages
    return total_no_packages


# The save_result function appends the information from a run to a results csv file
def save_result(
    scenario_id: int,
    strategy: str,
    results: Dict[str, Any],
    information: Dict[str, int],
    process_id: int,
):
    # Create a dictionary with the result data
    data: Dict[str, Any] = {
        "strategy": strategy,
        "scenario_id": scenario_id,
        "no_drones": information["no_drones"],
        "drone_capacity": information["drone_capacity"],
        "no_customers": information["no_customers"],
        "total_time": results["steps"][0],
        "package_delivery_time": results["steps"][1],
        "drone_travel_distance": round(results["drone_travel_distance"], 2),
        "truck_travel_distance": round(results["truck_travel_distance"], 2),
        "total_cluster_time": results["X1"],
        "total_active_time": results["X2"],
        "utilization": round(results["utilization"], 2),
        "avg_package_wait_time": round(
            results["total_package_waiting_time"] / information["no_packages_total"], 2
        ),
        "avg_customer_wait_time": round(
            results["total_customer_waiting_time"] / information["no_customers"], 2
        ),
        "total_delay_time": results["total_delay_time"],
        "avg_span_2": results["avg_span_2"],
        "avg_span_3": results["avg_span_3"],
        "avg_span_4": results["avg_span_4"],
        "avg_nodropoffs_2": results["avg_nodropoofs_2"],
        "avg_nodropoffs_3": results["avg_nodropoofs_3"],
        "avg_nodropoffs_4": results["avg_nodropoofs_4"],
        "no_preventions": results["no_preventions"],
        "no_battery_swaps": results["no_battery_swaps"],
        "no_clusters": results["no_clusters"],
    }

    # Validate the data against the schema
    for col in RESULTS_SCHEMA:
        if col["name"] in data:
            assert isinstance(
                data[col["name"]], col["type"]
            ), f"Invalid type for column '{col['name']}'"
        else:
            raise ValueError(f"Missing column '{col['name']}' in result data")

    # Create a DataFrame with the result data
    df = pd.DataFrame([data])

    filename: str = f"results/parallel/results_process_{process_id}.csv"
    # Append the result DataFrame to the existing CSV file
    df.to_csv(filename, mode="a", header=not os.path.exists(filename), index=False)
    # df.to_csv("results/results.csv", mode="a", header=False, index=False)


def initialise_results_file_with_columns(results_file_path: str):
    # Extract column names from the schema
    columns: List[str] = [col["name"] for col in RESULTS_SCHEMA]

    # Create an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=columns)

    # Save the empty DataFrame to a CSV file
    df.to_csv(results_file_path, index=False)
