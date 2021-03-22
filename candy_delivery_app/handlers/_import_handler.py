import abc
from django.core.exceptions import ValidationError
from ._request_handler import RequestWithContentHandler


# =====================================================================================================================


__all__ = [
    'ImportHandler',
    'ObjectValidationError',
]


# =====================================================================================================================


class ObjectValidationError(ValidationError):
    """
    Ошибка проверки корректности данных объекта
    """

    def __init__(self, object_id, *args, **kwargs):
        """
        Инциализация
        :param int object_id: id объекта
        :param args: аргументы родительского класса
        :param kwargs: именованные аргументы родительского класса
        """
        super().__init__(*args, **kwargs)
        self.object_id = object_id


# =====================================================================================================================


class ImportHandler(RequestWithContentHandler):
    """
    Обработчик запроса на добавление объектов
    """

    # Имя параметра, содержащего
    # список id в ответе
    _OUTPUT_KEY = 'objects'

    def _process(self, data):
        """
        Обработка запроса (специфическая часть)
        :param data: данные запроса
        """
        objects = list()
        invalid_ids = list()
        for item in data['data']:
            try:
                objects.append(self._init_object(item))
            except ObjectValidationError as e:
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
                imported_ids.append(self._save_object(object_))
            self._status = 201
            self._content = {
                self._OUTPUT_KEY: self.__create_ids_list(imported_ids),
            }

    @staticmethod
    @abc.abstractmethod
    def _init_object(item):
        """
        Формирование объекта по данным элемента запроса
        :param item: элемент запроса
        :return: объект
        """
        pass

    @staticmethod
    @abc.abstractmethod
    def _save_object(object_):
        """
        Запись объекта в БД
        :param object_: объект для записи
        :return int: идентификатор сохраненного объекта
        """
        pass

    @staticmethod
    def __create_ids_list(ids):
        """
        Формирование выходного списка id
        :param list(int) ids: список id
        :return list(dict): список id в формате [{"id": id1}, {"id": id2}, ...]
        """
        return [{'id': i} for i in ids]
