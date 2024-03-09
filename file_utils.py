from typing import List, Tuple


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
def save_result(scenario_id: int, strategy: str, results, information: Tuple[int, int]):

    with open("results/results.csv", "a", encoding="utf-8") as f:

        print_string = f"{strategy},{scenario_id},{information[0]},{information[1]},{','.join(str(res) for res in results)}\n"
        f.write(print_string)


def initialise_results_file_with_columns(results_file_path: str):
    # Before we begin the simulation we want to initialize the csv file which will store the results
    columns: str = (
        "strategy,scenario_id,drone_capacity,no_customers,total_time,package_delivery_time,drone_travel_distance,truck_travel_distance,total_cluster_time,total_active_time,utilization,avg_package_wait_time,avg_customer_wait_time,total_delay_time,avg_span_2,avg_span_3,avg_span_4,avg_nodropoffs_2,avg_nodropoffs_3,avg_nodropoffs_4,no_preventions\n"
    )
    with open(results_file_path, "w", encoding="utf-8") as f:
        f.write(columns)
