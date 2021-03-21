import abc
from ._request_handler import RequestHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportHandler',
]


# =====================================================================================================================


class ImportHandler(RequestHandler):
    """
    Обработчик запроса на добавление объектов
    """

    _OUTPUT_KEY = 'objects'

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process(self, data):
        objects = list()
        invalid_ids = list()
        for item in data['data']:
            try:
                objects.append(self._init_object(item))
            except models.ObjectValidationError as e:
                invalid_ids.append(e.object_id)

        if len(invalid_ids) > 0:
            self._status = 400
            self._content = {
                'validation_error': {
                    self._OUTPUT_KEY: self.__create_ids_list(invalid_ids),
                },
            }
        else:
            imported_ids = list()
            for object_ in objects:
                self._save_object(object_)
                imported_ids.append(object_.id)
            self._status = 201
            self._content = {
                self._OUTPUT_KEY: self.__create_ids_list(imported_ids),
            }

    @staticmethod
    @abc.abstractmethod
    def _init_object(item):
        pass

    @staticmethod
    @abc.abstractmethod
    def _save_object(object_):
        pass

    @staticmethod
    def __create_ids_list(ids):
        return [{'id': i} for i in ids]
