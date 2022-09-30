from panther.logger import logger
from panther.db.connection import db
from panther.db.utils import query_logger


class BaseTinyDBQuery:

    @classmethod
    @query_logger
    def get_one(cls, _data: dict = None, /, **kwargs):
        from tinydb import Query
        if _data is None:
            _data = {}
        _data = {k: v for k, v in _data.items() if v not in [None]}
        kwargs = {k: v for k, v in kwargs.items() if v not in [None]}
        result = db.session.search(Query().fragment(_data | kwargs))
        if len(result) < 1:
            return None
        else:
            return result[0]

    @classmethod
    @query_logger
    def count(cls, _data: dict = None, /, **kwargs) -> None:
        logger.critical('count() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def list(cls, _data: dict = None, /, **kwargs):
        from tinydb import Query
        if _data is None:
            _data = {}
        _data = {k: v for k, v in _data.items() if v not in [None]}
        kwargs = {k: v for k, v in kwargs.items() if v not in [None]}
        return db.session.search(Query().fragment(_data | kwargs))

    @classmethod
    @query_logger
    def create(cls, _data: dict = None, **kwargs) -> int:
        return db.session.insert(_data | kwargs)

    @query_logger
    def delete(self) -> None:
        logger.critical('delete() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def delete_one(cls, **kwargs) -> None:
        logger.critical('delete_one() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def delete_many(cls, **kwargs) -> None:
        logger.critical('delete_many() is not supported while using TinyDB.')

    @query_logger
    def update(self, **kwargs) -> None:
        logger.critical('update() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def update_one(cls, _filter, _data: dict = None, /, **kwargs) -> None:
        logger.critical('update_one() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def update_many(cls, _filter, **kwargs) -> None:
        logger.critical('update_many() is not supported while using TinyDB.')

    @classmethod
    @query_logger
    def increment(cls, _filter, **kwargs) -> None:
        logger.critical('increment() is not supported while using TinyDB.')
