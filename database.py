from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError, NoResultFound
from constants import *


################################################################################
# engine
################################################################################

engine = create_engine(
    url = SQLALCHEMY_DATABASE_URL,
    connect_args = {"check_same_thread": False}
)


################################################################################
# model
################################################################################

DBModel = declarative_base()


class DBModelExt(DBModel):
    """Расширение для базовой модели. Добавляются конвертации в строку и словарь.
    """
    __abstract__ = True

    def __str__(self) -> str:
        return " / ".join(str(getattr(self, column.name)) \
            for column in self.__table__.columns)

    def to_dict(self):
        return {column.name: getattr(self, column.name) \
            for column in self.__table__.columns}


class DBUser(DBModelExt):
    """Таблица с пользователями.
    """
    __tablename__ = "users"

    id = Column(Integer, nullable = False, primary_key = True, autoincrement = True, index = True)
    login = Column(String, nullable = False, unique = True, index = True)
    password = Column(String, nullable = False,)
    items = relationship("DBItem", back_populates = "owner", passive_deletes = True)

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password


class DBItem(DBModelExt):
    """Таблица с объектами.
    """
    __tablename__ = "items"

    id = Column(Integer, nullable = False, primary_key = True, autoincrement = True, index = True)
    name = Column(String, nullable = False, unique = True, index = True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete = 'CASCADE'), nullable = False)
    owner = relationship("DBUser", back_populates = "items")

    def __init__(self, name: str, owner_id: int) -> None:
        self.name = name
        self.owner_id = owner_id


DBModel.metadata.create_all(engine)


################################################################################
# CRUD
################################################################################

DBSession = sessionmaker(autocommit = False, autoflush = False, bind = engine)


def db_clear_all() -> None:
    """Удалить все данные из таблиц БД.
    """
    global DBSession
    with DBSession() as session:
        session.query(DBItem).delete()
        session.query(DBUser).delete()
        session.commit()
    return None


def db_create_user(login: str, password: str) -> DBUser:
    """Создать нового пользователя.

    Args:
        login (str): Логин.
        password (str): Пароль.

    Raises:
        DuplicateValueError: Пользователь с заданным логином уже существует.

    Returns:
        DBUser: Пользователь в виде модели DBUser.
    """
    global DBSession
    with DBSession() as session:
        try:
            user = DBUser(login = login, password = password)
            session.add(user)
            session.commit()
            session.refresh(user)

            '''
            # alternative 1
            from sqlalchemy import insert
            cursor = session.execute(
                insert(DBUser).values(login = login, password = password))
            session.commit()
            user = session.get(DBUser, cursor.lastrowid)
            '''

            '''
            # alternative 2
            from sqlalchemy import insert
            cursor = session.execute(
                insert(DBUser), [{"login": login, "password": password}])
            session.commit()
            user = session.get(DBUser, cursor.lastrowid)
            '''
        except IntegrityError as exc:
            raise DuplicateValueError(login) from exc

    return user


def db_read_user(login: str) -> DBUser:
    """Зачитать пользователя по заданному логину.

    Args:
        login (str): Логин.

    Raises:
        NoValueFoundError: Пользователь с заданным логином не существует.

    Returns:
        DBUser: Пользователь в виде модели DBUser.
    """
    global DBSession
    with DBSession() as session:
        try:
            user = session.query(DBUser).filter(DBUser.login == login).one()

            '''
            # alternative 1
            from sqlalchemy import select
            user = session.execute(
                select(DBUser).where(DBUser.login == login)).scalar_one()
            '''
        except NoResultFound as exc:
            raise NoValueFoundError(login) from exc

    return user


def db_read_user_by_id(id: int) -> DBUser:
    """Зачитать пользователя по заданному идентификатору.

    Args:
        id (int): Идентификатор.

    Raises:
        NoValueFoundError: Пользователь с заданным идентификатором не существует.

    Returns:
        DBUser: Пользователь в виде модели DBUser.
    """
    global DBSession
    with DBSession() as session:
        try:
            user = session.query(DBUser).filter(DBUser.id == id).one()
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
    return user


def db_update_user(id: int, new_login: str, new_password: str) -> DBUser:
    """Обновить данные существующего пользователя.

    Args:
        id (int): Идентификатор - данные этого пользователя будут обновлены.
        new_login (str): Новый логин.
        new_password (str): Новый пароль.

    Raises:
        NoValueFoundError: Пользователь с заданным идентификатором не существует.
        DuplicateValueError: Пользователь с заданным новым логином уже существует.

    Returns:
        DBUser: Пользователь в виде модели DBUser.
    """
    global DBSession
    with DBSession() as session:
        try:
            user = session.query(DBUser).filter(DBUser.id == id).one()
            user.login = new_login
            user.password = new_password
            session.commit()
            session.refresh(user)

            '''
            # alternative 1 (no exception)
            session.query(DBUser).filter(DBUser.id == id). \
                update({"login": new_login, "password": new_password})
            session.commit()
            user = session.get(DBUser, id)
            '''

            '''
            # alternative 2 (no exception)
            from sqlalchemy import update
            session.execute(
                update(DBUser). \
                values(login = new_login, password = new_password). \
                where(DBUser.id == id))
            session.commit()
            user = session.get(DBUser, id)
            '''
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
        except IntegrityError as exc:
            raise DuplicateValueError(new_login) from exc

    return user


def db_delete_user(id: int) -> None:
    """Удалить пользователя по заданному идентификатору.

    Args:
        id (int): Идентификатор.

    Raises:
        NoValueFoundError: Пользователь с заданным идентификатором не существует.

    Returns:
        None: None
    """
    global DBSession
    with DBSession() as session:
        try:
            user = session.query(DBUser).filter(DBUser.id == id).one()
            session.delete(user)
            session.commit()

            '''
            # alternative 1 (no exception)
            session.query(DBUser).filter(DBUser.id == id).delete()
            session.commit()
            '''

            '''
            # alternative 2 (no exception)
            from sqlalchemy import delete
            session.execute(
                delete(DBUser).where(DBUser.id == id))
            session.commit()
            '''
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc

    return None


def db_user_list() -> list:
    """Получить список пользователей.

    Returns:
        list: Список пользователей в виде моделей DBUser.
    """
    global DBSession
    with DBSession() as session:
        user_list = session.query(DBUser)
    return user_list


def db_create_item(name: str, owner_id: int) -> DBItem:
    """Создать новый объект.

    Args:
        name (str): Наименование.
        owner_id (int): Идентификатор пользователя-владельца объекта.

    Raises:
        DuplicateValueError: Объект с заданным наименованием уже существует.

    Returns:
        DBItem: Объект в виде модели DBItem.
    """
    global DBSession
    with DBSession() as session:
        try:
            item = DBItem(name = name, owner_id = owner_id)
            session.add(item)
            session.commit()
            session.refresh(item)
        except IntegrityError as exc:
            raise DuplicateValueError(name) from exc
    return item


def db_read_item(name: str) -> DBItem:
    """Зачитать объект по заданному наименованию.

    Args:
        name (str): Наименование.

    Raises:
        NoValueFoundError: Объект с заданным наименованием не существует.

    Returns:
        DBItem: Объект в виде модели DBItem.
    """
    global DBSession
    with DBSession() as session:
        try:
            item = session.query(DBItem).filter(DBItem.name == name).one()
        except NoResultFound as exc:
            raise NoValueFoundError(name) from exc
    return item


def db_read_item_by_id(id: int) -> DBItem:
    """Зачитать объект по заданному идентификатору.

    Args:
        id (int): Идентификатор.

    Raises:
        NoValueFoundError: Объект с заданным идентификатором не существует.

    Returns:
        DBItem: Объект в виде модели DBItem.
    """
    global DBSession
    with DBSession() as session:
        try:
            item = session.query(DBItem).filter(DBItem.id == id).one()
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
    return item


def db_update_item(id: int, new_name: str, new_owner_id: int) -> DBItem:
    """Обновить данные существующего объекта.

    Args:
        id (int): Идентификатор - данные этого объекта будут обновлены.
        new_name (str): Новое наименование.
        new_owner_id (int): Новый пользователь-владелец объекта.

    Raises:
        NoValueFoundError: Объект с заданным идентификатором не существует.
        DuplicateValueError: Объект с заданным наименованием уже существует.

    Returns:
        DBItem: Объект в виде модели DBItem.
    """
    global DBSession
    with DBSession() as session:
        try:
            item = session.query(DBItem).filter(DBItem.id == id).one()
            item.name = new_name
            item.owner_id = new_owner_id
            session.commit()
            session.refresh(item)
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
        except IntegrityError as exc:
            raise DuplicateValueError(new_name) from exc
    return item


def db_delete_item(id: int) -> None:
    """Удалить объект по заданному идентификатору.

    Args:
        id (int): Идентификатор.

    Raises:
        NoValueFoundError: Объект с заданным идентификатором не существует.

    Returns:
        None: None
    """
    global DBSession
    with DBSession() as session:
        try:
            item = session.query(DBItem).filter(DBItem.id == id).one()
            session.delete(item)
            session.commit()
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
    return None


def db_rebase_item(id: int, new_owner_id: int) -> DBItem:
    """Перепривязать обеъкт от одного владельца к другому.

    Args:
        id (int): Идентификатор - этот объект будет перепривязан.
        new_owner_id (int): Идентификатор пользователя-нового-владельца объекта.

    Raises:
        NoValueFoundError: Объект с заданным идентификатором не существует.

    Returns:
        DBItem: Объект в виде модели DBItem.
    """
    global DBSession
    with DBSession() as session:
        try:
            item = session.query(DBItem).filter(DBItem.id == id).one()
            item.owner_id = new_owner_id
            session.commit()
            session.refresh(item)
        except NoResultFound as exc:
            raise NoValueFoundError(id) from exc
    return item


def db_item_list() -> list:
    """Получить список объектов.
    """
    global DBSession
    with DBSession() as session:
        item_list = session.query(DBItem)
    return item_list