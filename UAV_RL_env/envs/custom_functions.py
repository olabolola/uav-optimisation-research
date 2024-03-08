from typing import List, Tuple

import numpy as np
import gym
import matplotlib.pyplot as plt

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
        self.customer_positions: List[Tuple[int, ...]] = []

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

        # Check if we have finished delivering all the packages
        # We have two types of done.
        # 1) When the trucks return to the warehouse
        # 2) When all the packages are delivered
        self.done: List[bool] = [False, False]

    def step(self, actions: Tuple[List[str], ...]):

        # actions is a list containing two elements; a list of truck actions and a list of drone actions
        # for each truck and drone respectively

        # For now trucks either move towards a certain position or just stay still
        truck_actions: List[str] = actions[0]
        for truck, truck_action in zip(self.trucks, truck_actions):
            self._take_truck_action(truck, truck_action)

        # Action will be a list of actions for each drone
        drone_actions: List[str] = actions[1]
        for drone, drone_action in zip(self.drones, drone_actions):
            self._take_drone_action(drone, drone_action)

        for customer in self.customers:
            if customer.no_packages_still_on_truck < 0:
                logger.debug("Customer position: %s", customer.position)
            assert customer.no_packages_still_on_truck >= 0
            assert customer.no_of_packages >= 0
        # Now the observations
        # For now just make the observation be the list of trucks, drones and remaining customers

        truck_observation = (self.trucks,)
        drone_observation = (self.drones,)

        observation = (truck_observation, drone_observation, self.customers)

        # Check if we are done
        # First we check if there are no more customers to deliver to
        if len(self.unserviced_customers) == 0:

            self.done[1] = True

            self.done[0] = True
            # Here we make sure the truck has returned to the warehouse
            for truck in self.trucks:
                if truck.position != self.warehouse_position:
                    self.done[0] = False

        # Return reward, observation, done, info
        return observation, None, self.done, None

    # This function load the customer positions and number of packages for each customer

    def load_from_file(self):
        with open(self.load_file, "a+", encoding="utf-8") as file:
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

    def reset(self):

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
                drone = celes.Drone(celes.Position(x, y), capacity=self.drone_capacity, home_truck=truck)

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

        if action == "nothing":
            pass
        elif action == "go_to_position":
            drone.go_to_position(action[1])
        elif action == "return_to_home_truck":
            drone.go_to_home_truck()
        elif action == "deliver_next_package":
            # For now its just always this action
            if not drone.home_truck.is_moving:
                drone.deliver_next_package(self.unserviced_customers)
        elif action == "failsafe_mode":
            # TODO Do something???
            pass

        # TODO we check in the function but maybe only call for drones on truck?
        drone.charge()

    def _take_truck_action(self, truck: Truck, action: str):

        # TODO are we double counting here?
        # Each step we want to add 1 to the waiting time of the packages
        for cluster_packages in truck.packages.values():
            for package in cluster_packages:
                package.waiting_time += 1

        # For now action is a 2-tuple that tells the truck where to go to
        if action == "nothing":
            pass
        elif action == "go_to_next_cluster":

            truck.go_to_next_cluster()
