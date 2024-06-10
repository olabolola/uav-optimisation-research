import unittest
from UAV_RL_env.envs.celes import (
    Customer,
    get_package_for_customer_with_most_packages,
    Position,
)


class TestGetPackageForCustomerWithMostPackages(unittest.TestCase):

    def test_single_customer_with_most_packages(self):
        customer1 = Customer(1, 5)
        customer2 = Customer(2, 3)
        packages = [
            Package(1, customer1),
            Package(2, customer1),
            Package(3, customer2),
            Package(4, customer2),
            Package(5, customer2),
        ]
        position = Position(0, 0)
        result = get_package_for_customer_with_most_packages(position, packages)
        self.assertEqual(result.customer.id, 1)

    def test_multiple_customers_with_same_package_count(self):
        customer1 = Customer(1, 5)
        customer2 = Customer(2, 5)
        packages = [
            Package(1, customer1),
            Package(2, customer1),
            Package(3, customer2),
            Package(4, customer2),
        ]
        position = Position(0, 0)
        result = get_package_for_customer_with_most_packages(position, packages)
        self.assertIn(result.customer.id, [1, 2])

    def test_no_packages(self):
        packages = []
        position = Position(0, 0)
        result = get_package_for_customer_with_most_packages(position, packages)
        self.assertIsNone(result)

    def test_single_package(self):
        customer = Customer(1, 1)
        packages = [Package(1, customer)]
        position = Position(0, 0)
        result = get_package_for_customer_with_most_packages(position, packages)
        self.assertEqual(result.id, 1)

    def test_multiple_packages_same_customer(self):
        customer = Customer(1, 2)
        packages = [Package(1, customer), Package(2, customer)]
        position = Position(0, 0)
        result = get_package_for_customer_with_most_packages(position, packages)
        self.assertEqual(result.customer.id, 1)
        self.assertIn(result.id, [1, 2])


if __name__ == "__main__":
    unittest.main()
