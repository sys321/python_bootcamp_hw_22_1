import sys
import pytest
import requests
import database
from constants import API_URL

################################################################################
# py-tests
################################################################################

pytest.dump = {}


def test_00_init():
    database.db_clear_all()


def test_01_user_create():
    """Тест маршрута /registration.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    for user in [{"login": "admin", "password": "admin"},
                    {"login": "user_1", "password": "user_1_password"},
                    {"login": "user_2", "password": "user_2_password"},
                    {"login": "user_3", "password": "user_3_password"}]:
        response = requests.post(API_URL + "/registration", json = user)
        assert response != None
        assert response.status_code == 200

        data = response.json()
        assert data != None
        assert "status_code" in data
        assert "status_message" in data
        assert "data" in data
        assert data["status_code"] == "0"

        pytest.dump[user["login"] + '_id'] = data["data"]["id"]

    # попытка дублирования данных
    user = {"login": "admin", "password": "admin"}

    response = requests.post(API_URL + "/registration", json = user)
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "1"

    # попытка передачи некорректных данных
    user = {"aaa": "aaa"}

    response = requests.post(API_URL + "/registration", json = user)
    assert response != None
    assert response.status_code == 422


def test_02_user_login():
    """Тест маршрута /login.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    for user in [{"login": "admin", "password": "admin"},
                    {"login": "user_1", "password": "user_1_password"},
                    {"login": "user_2", "password": "user_2_password"},
                    {"login": "user_3", "password": "user_3_password"}]:
        response = requests.post(API_URL + "/login", json = user)
        assert response != None
        assert response.status_code == 200

        data = response.json()
        assert data != None
        assert "status_code" in data
        assert "status_message" in data
        assert "token" in data
        assert data["status_code"] == "0"

        pytest.dump[user["login"] + '_jwt'] = data["token"]

    # попытка подключения несуществующим пользователем
    user = {"login": "admin1", "password": "admin"}

    response = requests.post(API_URL + "/login", json = user)
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "2"

    # попытка подключения с неправильным паролем
    user = {"login": "admin", "password": "admin1"}

    response = requests.post(API_URL + "/login", json = user)
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "3"


def test_03_user_delete():
    """Тест маршрута /users/{id}.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.delete(
        API_URL + f"/users/{pytest.dump['user_3_id']}",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "0"

    # попытка удалить несуществующего пользователя
    response = requests.delete(
        API_URL + f"/users/{pytest.dump['user_3_id']}",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "2"

    # попытка подключения с неправильным токеном
    response = requests.delete(
        API_URL + f"/users/{pytest.dump['user_2_id']}",
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_04_user_list():
    """Тест маршрута /users.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.get(
        API_URL + "/users",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert "data" in data
    assert data["status_code"] == "0"
    assert isinstance(data["data"], list) == True
    assert len(data["data"]) == 3

    # попытка подключения с неправильным токеном
    response = requests.get(
        API_URL + "/users",
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_05_item_create():
    """Тест маршрута /items/new.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    for item in [{"name": "item_1", "owner_id": pytest.dump["admin_id"]},
                    {"name": "item_2", "owner_id": pytest.dump["admin_id"]},
                    {"name": "item_3", "owner_id": pytest.dump["user_1_id"]},
                    {"name": "item_4", "owner_id": pytest.dump["user_2_id"]}]:
        response = requests.post(
            API_URL + "/items/new",
            json = item,
            headers = {"token": pytest.dump["admin_jwt"]})
        assert response != None
        assert response.status_code == 200

        data = response.json()
        assert data != None
        assert "status_code" in data
        assert "status_message" in data
        assert "data" in data
        assert data["status_code"] == "0"

        pytest.dump[item["name"] + '_id'] = data["data"]["id"]

    # попытка дублирования данных
    item = {"name": "item_1", "owner_id": pytest.dump["admin_id"]}
    response = requests.post(
        API_URL + "/items/new",
        json = item,
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "1"

    # попытка объявить владельцем несуществующего пользователя
    # .. тут обнаружилось, что внешний ключ не работает ..

    # попытка передачи некорректных данных
    item = {"aaa": "aaa"}
    response = requests.post(
        API_URL + "/items/new",
        json = item,
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 422

    # попытка подключения с неправильным токеном
    item = {"name": "item_1", "owner_id": pytest.dump["admin_id"]}
    response = requests.post(
        API_URL + "/items/new",
        json = item,
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_06_item_delete():
    """Тест маршрута /items/{id}.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.delete(
        API_URL + f"/items/{pytest.dump['item_4_id']}",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "0"

    # попытка удалить несуществующий объект
    response = requests.delete(
        API_URL + f"/items/{pytest.dump['item_4_id']}",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "2"

    # попытка подключения с неправильным токеном
    response = requests.delete(
        API_URL + f"/items/{pytest.dump['item_3_id']}",
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_07_item_list():
    """Тест маршрута /items.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.get(
        API_URL + "/items",
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert "data" in data
    assert data["status_code"] == "0"
    assert isinstance(data["data"], list) == True
    assert len(data["data"]) == 3

    # попытка подключения с неправильным токеном
    response = requests.get(
        API_URL + "/items",
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_08_item_send():
    """Тест маршрута /send.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.post(
        API_URL + "/send",
        json = {"id": pytest.dump["item_2_id"], "new_owner_login": "user_2"},
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert "url" in data
    assert data["status_code"] == "0"

    pytest.dump["rebase_item_url"] = data["url"]

    # попытка послать чужой объект
    response = requests.post(
        API_URL + "/send",
        json = {"id": pytest.dump["item_3_id"], "new_owner_login": "user_2"},
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "5"

    # попытка послать несуществующий объект
    response = requests.post(
        API_URL + "/send",
        json = {"id": 100500, "new_owner_login": "user_1"},
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "2"

    # попытка послать несуществующему пользователю
    response = requests.post(
        API_URL + "/send",
        json = {"id": pytest.dump["item_1_id"], "new_owner_login": "Zzz"},
        headers = {"token": pytest.dump["admin_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "2"

    # попытка подключения с неправильным токеном
    response = requests.post(
        API_URL + "/send",
        json = {"id": pytest.dump["item_1_id"], "new_owner_login": "user_1"},
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


def test_09_item_get():
    """Тест маршрута /get.
    """
    # проверка вызова маршрута, наличия ответа и формата ответа
    response = requests.get(
        pytest.dump["rebase_item_url"],
        headers = {"token": pytest.dump["user_2_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert "data" in data
    assert data["status_code"] == "0"

    # попытка получить чужой объект
    response = requests.get(
        pytest.dump["rebase_item_url"],
        headers = {"token": pytest.dump["user_1_jwt"]})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "5"

    # попытка подключения с неправильным токеном
    response = requests.get(
        pytest.dump["rebase_item_url"],
        headers = {"token": "Zzz"})
    assert response != None
    assert response.status_code == 200

    data = response.json()
    assert data != None
    assert "status_code" in data
    assert "status_message" in data
    assert data["status_code"] == "4"


if __name__ == "__main__":
    sys.exit(pytest.main(["-v", "-x", "tests_pt.py"]))