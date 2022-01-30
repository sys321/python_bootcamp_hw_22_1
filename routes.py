from fastapi import APIRouter, Header, Body
import database
import auth
from schemas import *
from constants import *

################################################################################
# routes
################################################################################

router = APIRouter()


@router.get("/")
async def hello():
    return {"data": "None"}


def _user_create(login: str, password: str) -> dict:
    """Создать нового пользователя.

    Вынесено в отдельный метод, чтобы вызывать для разных маршрутов.

    Args:
        login (str): Логин.
        password (str): Пароль.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    try:
        user = database.db_create_user(login, password)
        result = {"status_code": "0", "status_message" : "Success", "data": user.to_dict()}
    except DuplicateValueError as exc:
        result = {"status_code": exc.code, "status_message" : str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message" : f"Something went wrong: {exc}"}
    return result


@router.post("/registration")
async def user_create(login: str = Body(...), password: str = Body(...)) -> dict:
    """Маршрут - зарегистрировать нового пользователя. POST-запрос (/registration).

    Args:
        login (str): Логин.
        password (str): Пароль.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    return _user_create(login, password)


@router.post("/registration_p")
async def user_create_p(user: SchemaUser) -> dict:
    """Маршрут - зарегистрировать нового пользователя. POST-запрос (/registration_p).
    
    Вариант с pydantic схемой.

    Args:
        user (SchemaUser): pydantic схема с логином и паролем внутри.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    return _user_create(user.login, user.password)


@router.post("/login")
async def user_login(login: str = Body(...), password: str = Body(...)) -> dict:
    """Маршрут - авторизовать пользователя. POST-запрос (/login).

    Args:
        login (str): Логин.
        password (str): Пароль.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "token": значение]}.
    """
    try:
        user = database.db_read_user(login)
        if user.password != password:
            raise AuthorizationError()
        result = {"status_code": "0", "status_message": "Success",
            "token": auth.jwt_encode({"user_id": user.id})}
    except NoValueFoundError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except AuthorizationError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result


@router.delete("/users/{id}")
async def user_delete(id: int, token: str = Header(None)) -> dict:
    """Маршрут - удалить пользователя. DELETE-запрос (/users/{id}).

    Args:
        id (int): Идентификатор - этот пользователь будет удалён.
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст}.
    """
    try:
        auth.jwt_validate(token)
        database.db_delete_user(id)
        result = {"status_code": "0", "status_message" : "Success"}
    except NoValueFoundError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result


@router.get("/users")
async def user_list(token: str = Header(None)) -> dict:
    """Маршрут - получить список пользователей. GET-запрос (/users).

    Args:
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    try:
        auth.jwt_validate(token)
        user_list = database.db_user_list()
        result = {"status_code": "0", "status_message" : "Success",
            "data": [user.to_dict() for user in user_list]}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result


def _item_create(name: str, owner_id: int, token: str) -> dict:
    """Создать новый объект.

    Вынесено в отдельный метод, чтобы вызывать для разных маршрутов.

    Args:
        name (str): Наименование.
        owner_id (int): Идентификатор пользователя-владельца.
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    try:
        auth.jwt_validate(token)
        item = database.db_create_item(name, owner_id)
        result = {"status_code": "0", "status_message" : "Success", "data": item.to_dict()}
    except DuplicateValueError as exc:
        result = {"status_code": exc.code, "status_message" : str(exc)}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message" : f"Something went wrong: {exc}"}
    return result


@router.post("/items/new")
async def item_create(name: str = Body(...), owner_id: int =  Body(...), token: str = Header(None)) -> dict:
    """Маршрут - создать новый объект. POST-запрос (/items/new").

    Args:
        name (str): Наименование.
        owner_id (int): Идентификатор пользователя-владельца.
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    return _item_create(name, owner_id, token)


@router.post("/items/new_p")
async def item_create(item: SchemaItem, token: str = Header(None)) -> dict:
    """Маршрут - создать новый объект. POST-запрос (/items/new_p").

    Вариант с pydantic схемой.

    Args:
        item (SchemaItem): pydantic схема с наименованием и ссылкой на пользователя внутри.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    return _item_create(item.name, item.owner_id, token)


@router.delete("/items/{id}")
async def item_delete(id: int, token: str = Header(None)) -> dict:
    """Маршрут - удалить объект. DELETE-запрос (/items/{id}).

    Args:
        id (int): Идентификтор - этот объект будет удалён.
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст}.
    """
    try:
        auth.jwt_validate(token)
        database.db_delete_item(id)
        result = {"status_code": "0", "status_message" : "Success"}
    except NoValueFoundError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result


@router.get("/items")
async def item_list(token: str = Header(None)) -> dict:
    """Маршрут - получить список объектов. GET-запрос (/items).

    Args:
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    try:
        auth.jwt_validate(token)
        item_list = database.db_item_list()
        result = {"status_code": "0", "status_message" : "Success",
            "data": [item.to_dict() for item in item_list]}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result


@router.post("/send")
async def item_send(id: int = Body(...), new_owner_login: str = Body(...), token: str = Header(None)) -> dict:
    """Маршрут - послать свой объект другому пользователю. POST-запрос (/send).

    Args:
        id (int): Идентификатор - этот объект будет послан.
        new_owner_login (str): Логин - этот пользователь станет новым владельцем.
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "url": ссылка]}.
    """
    try:
        token = auth.jwt_decode(token, ["user_id"])
        item = database.db_read_item_by_id(id)
        if token["user_id"] != item.owner_id:
            raise OwnerError(id)
        new_owner = database.db_read_user(new_owner_login)
        result = {"status_code": "0", "status_message" : "Success", "url": API_URL + \
            "/get/" + auth.jwt_encode({"item_id": id, "new_owner_id": new_owner.id})}
    except OwnerError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except NoValueFoundError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
        raise
    return result


@router.get("/get/{params}")
async def item_get(params: str, token: str = Header(None)) -> dict:
    """Маршрут - получить объект от другого пользователя. GET-запроса (/get).

    Args:
        params (str): Параметры получения объекта (часть сгенерированной в /send ссылки).
        token (str): Токен текущего пользователя.

    Returns:
        dict: {"status_code": число, "status_message" : текст[, "data": словарь]}.
    """
    try:
        token = auth.jwt_decode(token, ["user_id"])
        params = auth.jwt_decode(params, ["item_id", "new_owner_id"])
        if token["user_id"] != params["new_owner_id"]:
            raise OwnerError(params["item_id"])
        item = database.db_rebase_item(params["item_id"], params["new_owner_id"])
        result = {"status_code": "0", "status_message" : "Success", "data": item.to_dict()}
    except OwnerError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except NoValueFoundError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except TokenError as exc:
        result = {"status_code": exc.code, "status_message": str(exc)}
    except Exception as exc:
        result = {"status_code": "-1", "status_message": f"Something went wrong: {exc}"}
    return result
