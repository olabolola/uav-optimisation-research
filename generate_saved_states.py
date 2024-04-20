from typing import Tuple, Dict
import random
import pandas as pd

random.seed(42)

GRID_HEIGHT: int = 2000
GRID_WIDTH: int = 2000

no_customers_values: Tuple[int, ...] = (50, 100, 200, 400)
no_scenarios_per_no_customers: int = 10

probability_distribution_for_each_no_packages: Dict[int, float] = {
    1: 0.85,
    2: 0.09,
    3: 0.04,
    4: 0.02,
}

assert sum(probability_distribution_for_each_no_packages.values()) == 1

for no_customers in no_customers_values:
    for i in range(no_scenarios_per_no_customers + 1):
        customers = []
        coordinates_set = set()  # Set to store unique coordinates

        while len(customers) < no_customers:
            x_position = random.randint(0, GRID_WIDTH - 1)
            y_position = random.randint(0, GRID_HEIGHT - 1)

            if (x_position, y_position) not in coordinates_set:
                no_packages = random.choices(
                    list(probability_distribution_for_each_no_packages.keys()),
                    weights=list(
                        probability_distribution_for_each_no_packages.values()
                    ),
                )[0]

                customers.append(
                    {
                        "x_coordinate": x_position,
                        "y_coordinate": y_position,
                        "no_packages": no_packages,
                    }
                )
                coordinates_set.add(
                    (x_position, y_position)
                )  # Add coordinates to the set

        # Create a DataFrame from the customers list
        df = pd.DataFrame(customers)

        # Save DataFrame to CSV file
        filename = f"saved_states/saved_state_{no_customers}_{i}.csv"
        df.to_csv(filename, index=False)
