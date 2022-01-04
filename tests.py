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
        database.db_clear_all()
        cls.dump = {
            "admin_id": None,
            "user_1_id": None,
            "user_2_id": None,
            "user_3_id": None,
            "admin_jwt": None,
            "user_1_jwt": None,
            "user_2_jwt": None,
            "item_1_id": None,
            "item_2_id": None,
            "item_3_id": None,
            "item_4_id": None
        }

    def setUp(self) -> None:
        pass

    def tearDown(self) -> None:
        pass

    @classmethod
    def tearDownClass(cls) -> None:
        cls.dump = None


    def test_01_user_create(self):
        """Тест маршрута /registration.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        for user in [{"login": "admin", "password": "admin"},
                     {"login": "user_1", "password": "user_1_password"},
                     {"login": "user_2", "password": "user_2_password"},
                     {"login": "user_3", "password": "user_3_password"}]:
            response = requests.post(API_URL + "/registration", json = user)
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)

            data = response.json()
            self.assertIsNotNone(data)
            self.assertIn("status_code", data)
            self.assertIn("status_message", data)
            self.assertIn("data", data)
            self.assertEqual(data["status_code"], "0")

            self.dump[user["login"] + '_id'] = data["data"]["id"]

        # попытка дублирования данных
        user = {"login": "admin", "password": "admin"}

        response = requests.post(API_URL + "/registration", json = user)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "1")

        # попытка передачи некорректных данных
        user = {"aaa": "aaa"}

        response = requests.post(API_URL + "/registration", json = user)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 422)


    def test_02_user_login(self):
        """Тест маршрута /login.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        for user in [{"login": "admin", "password": "admin"},
                     {"login": "user_1", "password": "user_1_password"},
                     {"login": "user_2", "password": "user_2_password"},
                     {"login": "user_3", "password": "user_3_password"}]:
            response = requests.post(API_URL + "/login", json = user)
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)

            data = response.json()
            self.assertIsNotNone(data)
            self.assertIn("status_code", data)
            self.assertIn("status_message", data)
            self.assertIn("token", data)
            self.assertEqual(data["status_code"], "0")

            self.dump[user["login"] + '_jwt'] = data["token"]

        # попытка подключения несуществующим пользователем
        user = {"login": "admin1", "password": "admin"}

        response = requests.post(API_URL + "/login", json = user)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "2")

        # попытка подключения с неправильным паролем
        user = {"login": "admin", "password": "admin1"}

        response = requests.post(API_URL + "/login", json = user)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "3")


    def test_03_user_delete(self):
        """Тест маршрута /users/{id}.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.delete(
            API_URL + f"/users/{self.dump['user_3_id']}",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "0")

        # попытка удалить несуществующего пользователя
        response = requests.delete(
            API_URL + f"/users/{self.dump['user_3_id']}",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "2")

        # попытка подключения с неправильным токеном
        response = requests.delete(
            API_URL + f"/users/{self.dump['user_2_id']}",
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_04_user_list(self):
        """Тест маршрута /users.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.get(
            API_URL + "/users",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertIn("data", data)
        self.assertEqual(data["status_code"], "0")
        self.assertIsInstance(data["data"], list)
        self.assertEqual(len(data["data"]), 3)

        # попытка подключения с неправильным токеном
        response = requests.get(
            API_URL + "/users",
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_05_item_create(self):
        """Тест маршрута /items/new.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        for item in [{"name": "item_1", "owner_id": self.dump["admin_id"]},
                     {"name": "item_2", "owner_id": self.dump["admin_id"]},
                     {"name": "item_3", "owner_id": self.dump["user_1_id"]},
                     {"name": "item_4", "owner_id": self.dump["user_2_id"]}]:
            response = requests.post(
                API_URL + "/items/new",
                json = item,
                headers = {"token": self.dump["admin_jwt"]})
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)

            data = response.json()
            self.assertIsNotNone(data)
            self.assertIn("status_code", data)
            self.assertIn("status_message", data)
            self.assertIn("data", data)
            self.assertEqual(data["status_code"], "0")

            self.dump[item["name"] + '_id'] = data["data"]["id"]

        # попытка дублирования данных
        item = {"name": "item_1", "owner_id": self.dump["admin_id"]}
        response = requests.post(
            API_URL + "/items/new",
            json = item,
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "1")

        # попытка объявить владельцем несуществующего пользователя
        # .. тут обнаружилось, что внешний ключ не работает ..

        # попытка передачи некорректных данных
        item = {"aaa": "aaa"}
        response = requests.post(
            API_URL + "/items/new",
            json = item,
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 422)

        # попытка подключения с неправильным токеном
        item = {"name": "item_1", "owner_id": self.dump["admin_id"]}
        response = requests.post(
            API_URL + "/items/new",
            json = item,
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_06_item_delete(self):
        """Тест маршрута /items/{id}.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.delete(
            API_URL + f"/items/{self.dump['item_4_id']}",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "0")

        # попытка удалить несуществующий объект
        response = requests.delete(
            API_URL + f"/items/{self.dump['item_4_id']}",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "2")

        # попытка подключения с неправильным токеном
        response = requests.delete(
            API_URL + f"/items/{self.dump['item_3_id']}",
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_07_item_list(self):
        """Тест маршрута /items.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.get(
            API_URL + "/items",
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertIn("data", data)
        self.assertEqual(data["status_code"], "0")
        self.assertIsInstance(data["data"], list)
        self.assertEqual(len(data["data"]), 3)

        # попытка подключения с неправильным токеном
        response = requests.get(
            API_URL + "/items",
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_08_item_send(self):
        """Тест маршрута /send.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.post(
            API_URL + "/send",
            json = {"id": self.dump["item_2_id"], "new_owner_login": "user_2"},
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertIn("url", data)
        self.assertEqual(data["status_code"], "0")

        self.dump["rebase_item_url"] = data["url"]

        # попытка послать чужой объект
        response = requests.post(
            API_URL + "/send",
            json = {"id": self.dump["item_3_id"], "new_owner_login": "user_2"},
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "5")

        # попытка послать несуществующий объект
        response = requests.post(
            API_URL + "/send",
            json = {"id": 100500, "new_owner_login": "user_1"},
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "2")

        # попытка послать несуществующему пользователю
        response = requests.post(
            API_URL + "/send",
            json = {"id": self.dump["item_1_id"], "new_owner_login": "Zzz"},
            headers = {"token": self.dump["admin_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "2")

        # попытка подключения с неправильным токеном
        response = requests.post(
            API_URL + "/send",
            json = {"id": self.dump["item_1_id"], "new_owner_login": "user_1"},
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


    def test_09_item_get(self):
        """Тест маршрута /get.
        """
        # проверка вызова маршрута, наличия ответа и формата ответа
        response = requests.get(
            self.dump["rebase_item_url"],
            headers = {"token": self.dump["user_2_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertIn("data", data)
        self.assertEqual(data["status_code"], "0")

        # попытка получить чужой объект
        response = requests.get(
            self.dump["rebase_item_url"],
            headers = {"token": self.dump["user_1_jwt"]})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "5")

        # попытка подключения с неправильным токеном
        response = requests.get(
            self.dump["rebase_item_url"],
            headers = {"token": "Zzz"})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIsNotNone(data)
        self.assertIn("status_code", data)
        self.assertIn("status_message", data)
        self.assertEqual(data["status_code"], "4")


if __name__ == "__main__":
    try:
        unittest.main(verbosity = 2, failfast = True)
    except SystemExit as exc:
        sys.exit(int(exc.code))
