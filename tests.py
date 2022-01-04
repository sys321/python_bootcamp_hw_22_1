import sys
import unittest
import requests
import database
from constants import API_URL

################################################################################
# unit-tests
################################################################################

class TestAPI(unittest.TestCase):
    """Юнит-тесты.
    """

    @classmethod
    def setUpClass(cls) -> None:
        pass

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        pass


    def test_01_user_create(self):
        """Тест маршрута /registration.
        """
        pass


if __name__ == "__main__":
    try:
        unittest.main(verbosity = 2, failfast = True)
    except SystemExit as exc:
        sys.exit(0)
