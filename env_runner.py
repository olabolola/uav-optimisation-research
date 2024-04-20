from typing import List, Dict

import gymnasium as gym


class EnvRunner:

    @staticmethod
    def run_env(
        run_number: int = 0,
        no_trucks: int = 2,
        no_clusters: int = 2,
        no_drones: int = 3,
        no_customers: int = 60,
        p: List[float] = [1],
        load: bool = False,
        load_file: str = "saved_states/saved_state_50_5.txt",
        strategy: str = "farthest_package_first",
        save_state: bool = False,
        drone_capacity: int = 2,
    ):

        env = gym.make(
            "HDS-v1",
            no_customers=no_customers,
            no_trucks=no_trucks,
            no_drones=no_drones,
            no_clusters=no_clusters,
            file_suffix=run_number,
            p=p,
            load=load,
            load_file=load_file,
            strategy=strategy,
            save_state=save_state,
            drone_capacity=drone_capacity,
        )

        env.reset(seed=42)

        truck_actions = []
        drone_actions = []

        truck_actions = ["go_to_next_cluster"] * no_trucks
        drone_actions = ["deliver_next_package"] * (no_trucks * no_drones)

        # Convert actions to tuple
        action = (truck_actions, drone_actions)

        total_time: int = (
            0  # Here we store the number of steps for the trucks to return to the warehouse
        )
        A: int = 0  # Here we store the number of steps until all packages are delivered

        # steps[0] will store the total time, while steps[1] will store the time it takes
        steps = [0, 0]

        render_cnt = 0
        while True:

            done: bool
            obs, _, done, _, info = env.step(action)
            total_time += 1

            # if there are still unservices customers then A++
            if info["no_unserviced_customers"] != 0:
                A += 1

            # if render_cnt % 17 == 0:
            #     env.render()
            # render_cnt += 1

            # When we are finished (trucks return to warehouse) we will return the results of the run
            if done:

                # After the simulation is over store the total number of steps and A
                steps[0] = total_time
                steps[1] = A

                drone_travel_distance = 0
                truck_travel_distance = 0

                X1 = 0  # X1 is the total time spent by trucks in clusters
                X2 = 0  # X2 is the total active time of drones (including 2 minute dropoff time)

                # This is sum of time for each package to reach the customer
                total_package_waiting_time = 0
                total_customer_waiting_time = 0

                # Total amount of time spent in the 2 min delay while delivering package
                total_delay_time = 0

                # The span is the time between the inital and final package deliveries for each customer
                # We store seperate values for each original_no_packages
                # Spans will be a dict with original_no_packages as the key and the total span as the value
                spans: Dict[int, int] = {2: 0, 3: 0, 4: 0}

                # Here we store the sum of the number of dropoffs for each customer grouped by original_no_packages
                no_dropoffs: Dict[int, int] = {2: 0, 3: 0, 4: 0}

                # How many times drones were prevented from leaving the truck due to battery constraints
                no_preventions: int = 0

                drones = obs["drone_observations"]
                trucks = obs["truck_observations"]
                customers = obs["customer_observations"]

                for customer in customers:
                    if customer["original_no_packages"] in spans.keys():
                        spans[customer["original_no_packages"]] += (
                            customer["customer_time_final"]
                            - customer["customer_time_initial"]
                        )
                        no_dropoffs[customer["original_no_packages"]] += customer[
                            "customer_no_dropoffs"
                        ]

                for drone in drones:
                    drone_travel_distance += drone["total_travel_distance"]
                    X2 += drone["total_active_time"]
                    total_delay_time += drone["total_delay_time"]
                    no_preventions += drone["no_preventions"]

                for truck in trucks:
                    total_package_waiting_time += truck["total_package_waiting_time"]
                    total_customer_waiting_time += truck["total_customer_waiting_time"]
                    truck_travel_distance += truck["total_travel_distance"]
                    X1 += truck["total_time_in_cluster"]

                utilization: float = X2 / (X1 * no_drones)

                no_battery_swaps: int = sum(
                    [drone["no_battery_swaps"] for drone in drones]
                )
                results: Dict = {
                    "steps": steps,
                    "drone_travel_distance": drone_travel_distance,
                    "truck_travel_distance": truck_travel_distance,
                    "X1": X1,
                    "X2": X2,
                    "utilization": utilization,
                    "total_package_waiting_time": total_package_waiting_time,
                    "total_customer_waiting_time": total_customer_waiting_time,
                    "total_delay_time": total_delay_time,
                    "spans": spans,
                    "no_dropoffs": no_dropoffs,
                    "no_preventions": no_preventions,
                    "no_battery_swaps": no_battery_swaps,
                }
                return results
