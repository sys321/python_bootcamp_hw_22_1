SQLALCHEMY_DATABASE_URL = "sqlite:///site.db"

API_URL = "http://localhost:8000"


class Error(Exception):
    """Базовый класс для всех исключений.
    """
    code = None


class DuplicateValueError(Error):
    """Не удалось обновить значение в таблице, значение дублируется.
    """
    def __init__(self, value):
        self.code = "1"
        self.value = value

    def __str__(self):
        return f"Value '{self.value}' already exists"


class NoValueFoundError(Error):
    """Не удалось найти значение в таблице, значение не существует.
    """
    def __init__(self, value):
        self.code = "2"
        self.value = value

    def __str__(self):
        return f"Value '{self.value}' not found"


class AuthorizationError(Error):
    """Не удалось пройти авторизацию, неверные логин или пароль.
    """
    def __init__(self):
        self.code = "3"

    def __str__(self):
        return "Invalid username or password"


class TokenError(Error):
    """Не удалось декодировать токен.
    """
    def __init__(self):
        self.code = "4"

    def __str__(self):
        return "JWT token failed signature validation"


class OwnerError(Error):
    """Не удалось перепривязать объект от одного владельца к другому.
    """
    def __init__(self, value):
        self.code = "5"
        self.value = value

    def __str__(self):
        return f"Item '{self.value}' is owned by another user"