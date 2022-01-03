import jwt
from jwt import DecodeError
from constants import TokenError


def jwt_encode(data: dict) -> str:
    """Поместить данные в jwt.

    Args:
        data (dict): Данные.

    Returns:
        str: jwt.
    """
    return jwt.encode(data, "secret_key", algorithm = "HS256")


def jwt_decode(token: str, keys: list = []) -> dict:
    """Извлечь данные из jwt.

    Args:
        token (str): Токен.
        keys (list, optional): Какие ключи должны быть внутри данных.
            Опциональная проверка.

    Raises:
        TokenError: Не удалось декодировать jwt либо данные внутри неформат.

    Returns:
        dict: Словарь с данными, какие были внутри Не удалось декодировать jwt.
    """
    try:
        data = jwt.decode(token, "secret_key", algorithms = ["HS256"])
        for key in keys:
            if key not in data:
                raise DecodeError
    except DecodeError as exc:
        raise TokenError() from exc
    return data


def jwt_validate(token: str) -> None:
    """Проверить jwt на валидность.

    Args:
        token (str): Токен.

    Raises:
        TokenError: Не удалось декодировать jwt.

    Returns:
        None: None
    """
    try:
        jwt.decode(token, "secret_key", algorithms = ["HS256"])
    except DecodeError as exc:
        raise TokenError() from exc
    return None


