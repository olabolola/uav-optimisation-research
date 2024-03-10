from typing import List, Tuple

import numpy as np
import gymnasium as gym
import matplotlib.pyplot as plt
from gymnasium import spaces

from logger_setup import logger
from . import celes
from .celes import Drone, Truck

# Width and height of the grid on witch our customers live

GRID_WIDTH = 2000
GRID_HEIGHT = 2000


class custom_class(gym.Env):

    def __init__(
        self,
        no_customers: int,
        no_trucks: int,
        no_drones: int,
        no_clusters: int,
        file_suffix: str,
        p: List[int],
        load: bool,
        load_file: str,
        strategy: str,
        save_state: bool,
        drone_capacity: int,
    ):

        # Indicates if we want to save our run or not
        self.save_state: bool = save_state

        # Strategy parameters for all trucks
        self.strategy: str = strategy

        # For loading from a file
        # load is a boolean that indicates whether or not we want to load from a file or not
        self.load: bool = load
        self.load_file: str = load_file

        # For making the video
        self.i: int = 0

        # For saving to a file
        self.file_suffix: str = file_suffix

        # Number of clusters
        self.no_clusters: int = no_clusters

        super().__init__()

        # Warehouse initialization
        self.warehouse_position: celes.Position = celes.Position(
            GRID_WIDTH // 2, GRID_HEIGHT // 2
        )
        self.warehouse: celes.Warehouse = celes.Warehouse(self.warehouse_position)

        # Customer initialization
        self.no_customers: int = no_customers
        self.customers: List[celes.Customer] = []
        self.unserviced_customers: List[celes.Customer] = []
        self.customer_positions: List[celes.Position] = []

        # TODO dont duplicate between reset and here
        if self.load:
            self.no_customers = (
                len(open(self.load_file, encoding="utf-8").readlines()) - 1
            )

        # Probability distribution for the packages
        self.p: List[int] = p

        # Truck and drone initialization
        self.no_trucks: int = no_trucks
        self.trucks: List[celes.Truck] = []

        self.no_drones: int = no_drones
        self.drones: List[celes.Drone] = []

        # Number of packages our drone can carry
        self.drone_capacity: int = drone_capacity

        # For clustering
        self.centroids = None

        # TODO add sensible bounds for these observations
        # Assuming no_trucks, no_drones, and no_customers are defined elsewhere in your code
        # Define observation space for truck observations
        truck_observation_space = spaces.Dict(
            {
                "total_package_waiting_time": spaces.Box(
                    low=0, high=float("inf"), shape=()
                ),
                "total_customer_waiting_time": spaces.Box(
                    low=0, high=float("inf"), shape=()
                ),
                "total_travel_distance": spaces.Box(low=0, high=float("inf"), shape=()),
                "total_time_in_cluster": spaces.Box(low=0, high=float("inf"), shape=()),
            }
        )

        # Define observation space for drone observations
        drone_observation_space = spaces.Dict(
            {
                "total_travel_distance": spaces.Box(low=0, high=float("inf"), shape=()),
                "total_active_time": spaces.Box(low=0, high=float("inf"), shape=()),
                "total_delay_time": spaces.Box(low=0, high=float("inf"), shape=()),
                "no_preventions": spaces.Box(low=0, high=float("inf"), shape=()),
            }
        )

        # Define observation space for customer observations
        customer_observation_space = spaces.Dict(
            {
                "original_no_packages": spaces.Box(low=0, high=float("inf"), shape=()),
                "customer_time_initial": spaces.Box(low=0, high=float("inf"), shape=()),
                "customer_time_final": spaces.Box(low=0, high=float("inf"), shape=()),
                "customer_no_dropoffs": spaces.Box(low=0, high=float("inf"), shape=()),
            }
        )

        # Create observation space for variable number of entities
        self.observation_space = spaces.Dict(
            {
                "truck_observations": spaces.Tuple(
                    [truck_observation_space] * self.no_trucks
                ),
                "drone_observations": spaces.Tuple(
                    [drone_observation_space] * self.no_drones * self.no_trucks
                ),
                "customer_observations": spaces.Tuple(
                    [customer_observation_space] * self.no_customers
                ),
            }
        )

        self.action_space = spaces.Discrete(2)

        # Check if we have finished delivering all the packages
        # We have two types of done.
        # 1) When the trucks return to the warehouse
        # 2) When all the packages are delivered
        self.done: bool = False

    def step(self, action: Tuple[List[str], ...]):

        # actions is a list containing two elements; a list of truck actions and a list of drone actions
        # for each truck and drone respectively

        # For now trucks either move towards a certain position or just stay still
        truck_actions: List[str] = action[0]
        for truck, truck_action in zip(self.trucks, truck_actions):
            self._take_truck_action(truck, truck_action)

        # Action will be a list of actions for each drone
        drone_actions: List[str] = action[1]
        for drone, drone_action in zip(self.drones, drone_actions):
            self._take_drone_action(drone, drone_action)

        for customer in self.customers:
            if customer.no_packages_still_on_truck < 0:
                logger.debug("Customer position: %s", customer.position)
            assert customer.no_packages_still_on_truck >= 0
            assert customer.no_of_packages >= 0
        # Now the observations
        # For now just make the observation be the list of trucks, drones and remaining customers

        observations = generate_observations(self.trucks, self.drones, self.customers)
        # Check if we are done
        # First we check if there are no more customers to deliver to
        if len(self.unserviced_customers) == 0:

            self.done = True

            # Here we make sure the truck has returned to the warehouse
            for truck in self.trucks:
                if truck.position != self.warehouse_position:
                    self.done = False

        # Return reward, observation, done, info
        return (
            observations,
            0,
            self.done,
            False,
            {"no_unserviced_customers": len(self.unserviced_customers)},
        )

    # This function load the customer positions and number of packages for each customer

    def load_from_file(self):
        with open(self.load_file, "r", encoding="utf-8") as file:
            lines = file.readlines()
            self.no_customers = len(lines) - 1

            if self.no_customers == 50:
                self.no_clusters = 2
            else:
                self.no_clusters = max(1, self.no_customers // 50)

            for line in lines[1:]:
                x_coord, y_coord, no_packages = line.split(", ")
                x_coord = int(x_coord)
                y_coord = int(y_coord)
                no_packages = int(no_packages)
                customer_position = celes.Position(x_coord, y_coord)
                customer = celes.Customer(customer_position, "apt")

                for _ in range(no_packages):
                    package = celes.Package(customer)
                    customer.add_package(package)

                self.customers.append(customer)

    def reset(self, options={}, seed=None):

        # Initialization
        self.customers = []
        self.customer_positions = []

        self.trucks = []
        self.drones = []

        # Truck and drone initialization

        for i in range(self.no_trucks):

            x = self.warehouse_position.x
            y = self.warehouse_position.y
            position = celes.Position(x, y)

            truck = celes.Truck(
                position,
                truck_id=i,
                total_no_drones=self.no_drones,
                strategy=self.strategy,
            )

            for _ in range(self.no_drones):
                drone = celes.Drone(
                    celes.Position(x, y), capacity=self.drone_capacity, home_truck=truck
                )

                truck.load_drone(drone)
                self.drones.append(drone)

            self.trucks.append(truck)

        # First check if we want to load from a file
        if self.load:
            self.load_from_file()
            self.warehouse.cluster_and_colour(
                self.customers, self.trucks, self.no_clusters
            )
            self.unserviced_customers = self.customers[:]
            return

        # Customer initialization
        for _ in range(self.no_customers):

            x = np.random.randint(1, GRID_WIDTH)
            y = np.random.randint(1, GRID_HEIGHT)
            position = celes.Position(x, y)
            while position in self.customer_positions:
                x = np.random.randint(1, GRID_WIDTH)
                y = np.random.randint(1, GRID_HEIGHT)
                position = celes.Position(x, y)
            self.customer_positions.append(position)
            customer = celes.Customer(position, "apt")

            # Packages are distributed between customer according to the distribution p.
            no_of_packages = np.random.choice(np.arange(1, len(self.p) + 1), p=self.p)
            for _ in range(no_of_packages):
                package = celes.Package(customer)
                customer.add_package(package)

            self.customers.append(customer)

        # cluster customers, and distribute packages accordingly
        self.warehouse.cluster_and_colour(self.customers, self.trucks, self.no_clusters)

        self.unserviced_customers = self.customers[:]

        # Here we save the state of our system
        if self.save_state:

            with open(
                f"saved_states/saved_state_{self.no_customers}_{self.file_suffix}.txt",
                "w",
                encoding="utf-8",
            ) as f:
                f.write("x_coordinate,y_coordinate,no_packages\n")
                for customer in self.customers:
                    f.write(
                        str(customer.position)
                        + ", "
                        + str(customer.no_of_packages)
                        + "\n"
                    )

        observations = generate_observations(self.trucks, self.drones, self.customers)
        return tuple([observations, {}])

    def render(self, mode: str = "human", close: bool = False):

        customer_x = []
        customer_y = []

        for customer in self.customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)

        truck_x = []
        truck_y = []
        for truck in self.trucks:
            truck_x.append(truck.position.x)
            truck_y.append(truck.position.y)

        drone_x = []
        drone_y = []

        for drone in self.drones:
            drone_x.append(drone.position.x)
            drone_y.append(drone.position.y)

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        for customer in self.unserviced_customers:
            ax1.scatter(
                customer.position.x,
                customer.position.y,
                c=customer.colour,
                alpha=0.5,
                label="customer",
            )
        drone_plot = ax1.scatter(drone_x, drone_y, c="b", label="drone", marker=".")
        truck_plot = ax1.scatter(truck_x, truck_y, c="g", label="truck", marker=",")

        # plt.legend((drone_plot, truck_plot), ("drone", "truck"), loc = "lower left")
        plt.xlim(-10, GRID_WIDTH)
        plt.ylim(-10, GRID_HEIGHT)

        plt.show()

    def _take_drone_action(self, drone: Drone, action: str):

        # TODO are we double counting here?
        # Each step we want to add 1 to the waiting time of the packages
        for package in drone.packages:
            package.waiting_time += 1

        # TODO removed steadystate consumption
        if drone.waiting:
            drone.steadystate_consumption()

        if action == "deliver_next_package":
            # For now its just always this action
            if not drone.home_truck.is_moving:
                drone.deliver_next_package(self.unserviced_customers)
        else:
            raise NotImplementedError("Unrecognised drone action.")

        # TODO we check in the function but maybe only call for drones on truck?
        drone.charge()

    def _take_truck_action(self, truck: Truck, action: str):

        # TODO are we double counting here?
        # Each step we want to add 1 to the waiting time of the packages
        for cluster_packages in truck.packages.values():
            for package in cluster_packages:
                package.waiting_time += 1

        # For now action is a 2-tuple that tells the truck where to go to
        if action == "go_to_next_cluster":
            truck.go_to_next_cluster()
        else:
            raise NotImplementedError("Unrecognised truck action.")


def generate_observations(
    trucks: List[celes.Truck],
    drones: List[celes.Drone],
    customers: List[celes.Customer],
):
    # Collect truck observations
    truck_observations = []
    for truck in trucks:
        truck_observations.append(
            {
                "total_package_waiting_time": truck.total_package_waiting_time,
                "total_customer_waiting_time": truck.total_customer_waiting_time,
                "total_travel_distance": truck.total_travel_distance,
                "total_time_in_cluster": truck.total_time_in_cluster,
            }
        )

    # Collect drone observations
    drone_observations = []
    for drone in drones:
        drone_observations.append(
            {
                "total_travel_distance": drone.total_travel_distance,
                "total_active_time": drone.total_active_time,
                "total_delay_time": drone.total_delay_time,
                "no_preventions": drone.no_preventions,
            }
        )

    # Collect customer observations
    customer_observations = []
    for customer in customers:
        customer_observations.append(
            {
                "original_no_packages": customer.original_no_packages,
                "customer_time_final": customer.time_final,
                "customer_time_initial": customer.time_initial,
                "customer_no_dropoffs": customer.no_dropoffs,
            }
        )

    return {
        "truck_observations": truck_observations,
        "drone_observations": drone_observations,
        "customer_observations": customer_observations,
    }
