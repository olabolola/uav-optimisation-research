import os
from typing import Any

import pandas as pd

# Define the schema for the results DataFrame
RESULTS_SCHEMA: list[dict[str, Any]] = [
    {"name": "strategy", "type": str},
    {"name": "scenario_id", "type": int},
    {"name": "no_drones", "type": int},
    {"name": "drone_capacity", "type": int},
    {"name": "no_customers", "type": int},
    {"name": "no_clusters", "type": int},
    {"name": "Total Distribution Time", "type": int},
    {"name": "Total Time to Deliver All Packages", "type": int},
    {"name": "Drones Travel Distance", "type": float},
    {"name": "Trucks Travel Distance", "type": float},
    {"name": "Trucks In-Cluster time", "type": int},
    {"name": "Drones Active Time", "type": int},
    {"name": "Drone Utilization", "type": float},
    {"name": "Total Package Delivery Time", "type": float},
    {"name": "Total Customer Delivery Time", "type": float},
    {"name": "Average Package Delivery Time", "type": float},
    {"name": "Average Customer Delivery Time", "type": float},
    {"name": "Median Package Delivery Time", "type": float | int},
    {"name": "Median Customer Delivery Time", "type": float | int},
    {"name": "avg_span_2", "type": float},
    {"name": "avg_span_3", "type": float},
    {"name": "avg_span_4", "type": float},
    {"name": "avg_nodropoffs_2", "type": float},
    {"name": "avg_nodropoffs_3", "type": float},
    {"name": "avg_nodropoffs_4", "type": float},
    {"name": "median_span_2", "type": float | int},
    {"name": "median_span_3", "type": float | int},
    {"name": "median_span_4", "type": float | int},
    {"name": "median_nodropoffs_2", "type": float | int},
    {"name": "median_nodropoffs_3", "type": float | int},
    {"name": "median_nodropoffs_4", "type": float | int},
    {"name": "no_of_customers_with_1_package", "type": int},
    {"name": "no_of_customers_with_2_package", "type": int},
    {"name": "no_of_customers_with_3_package", "type": int},
    {"name": "no_of_customers_with_4_package", "type": int},
    {"name": "The Number of Battery Swaps", "type": int},
]


def get_no_packages_per_category(filename: str, keys: list[int]) -> dict[int, int]:
    no_packages_per_category = {no: 0 for no in keys}
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            no_packages = int(line.split(",")[-1])
            if no_packages > 1:
                no_packages_per_category[no_packages] += no_packages
    return no_packages_per_category


def get_no_customers_per_no_packages(filename: str, keys: list[int]) -> dict[int, int]:
    no_customers_per_no_packages = {no: 0 for no in keys}
    with open(filename, encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            no_packages = int(line.split(",")[-1])
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
    results: dict[str, Any],
    information: dict[str, int],
    process_id: int,
):
    # Create a dictionary with the result data
    data: dict[str, Any] = {
        "strategy": strategy,
        "scenario_id": scenario_id,
        "no_drones": information["no_drones"],
        "drone_capacity": information["drone_capacity"],
        "no_customers": information["no_customers"],
        "no_clusters": results["no_clusters"],
        "Total Distribution Time": results["steps"][0],
        "Drones Travel Distance": round(results["drone_travel_distance"], 2),
        "Trucks Travel Distance": round(results["truck_travel_distance"], 2),
        "Trucks In-Cluster time": results["Trucks In-Cluster time"],
        "Drones Active Time": results["Drones Active Time"],
        "Drone Utilization": round(results["Drone Utilization"], 2),
        "avg_span_2": results["avg_span_2"],
        "avg_span_3": results["avg_span_3"],
        "avg_span_4": results["avg_span_4"],
        "avg_nodropoffs_2": results["avg_nodropoofs_2"],
        "avg_nodropoffs_3": results["avg_nodropoofs_3"],
        "avg_nodropoffs_4": results["avg_nodropoofs_4"],
        "median_span_2": results["avg_span_2"],
        "median_span_3": results["avg_span_3"],
        "median_span_4": results["avg_span_4"],
        "median_nodropoffs_2": results["avg_nodropoofs_2"],
        "median_nodropoffs_3": results["avg_nodropoofs_3"],
        "median_nodropoffs_4": results["avg_nodropoofs_4"],
        "The Number of Battery Swaps": results["no_battery_swaps"],
        "Total Time to Deliver All Packages": results["steps"][1],
        "Total Package Delivery Time": results["Total Package Delivery Time"],
        "Total Customer Delivery Time": results["Total Customer Delivery Time"],
        "Average Customer Delivery Time": results["average_customer_waiting_time"],
        "Average Package Delivery Time": results["average_package_waiting_time"],
        "Median Package Delivery Time": results["median_package_waiting_time"],
        "Median Customer Delivery Time": results["median_customer_waiting_time"],
        "no_of_customers_with_1_package": results["no_of_customers_with_1_package"],
        "no_of_customers_with_2_package": results["no_of_customers_with_2_package"],
        "no_of_customers_with_3_package": results["no_of_customers_with_3_package"],
        "no_of_customers_with_4_package": results["no_of_customers_with_4_package"],
    }

    # Validate the data against the schema
    for col in RESULTS_SCHEMA:
        if col["name"] in data:
            assert isinstance(data[col["name"]], col["type"]), (
                f"Invalid type for column '{col['name']}' expected '{col['type']}' got '{type(data[col['name']])}'"
            )
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
    columns: list[str] = [col["name"] for col in RESULTS_SCHEMA]

    # Create an empty DataFrame with the specified columns
    df = pd.DataFrame(columns=columns)

    # Save the empty DataFrame to a CSV file
    df.to_csv(results_file_path, index=False)
