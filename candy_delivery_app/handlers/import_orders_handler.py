from django.core.exceptions import ValidationError
from ._import_handler import ImportHandler, ObjectValidationError
from ..wrappers import OrderWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportOrdersHandler',
]


# =====================================================================================================================


class ImportOrdersHandler(ImportHandler):
    """
    Обработчик запроса на добавление заказов
    """

    # Имя параметра, содержащего
    # список id в ответе
    _OUTPUT_KEY = 'orders'

    @staticmethod
    def _init_object(item):
        """
        Формирование объекта по данным элемента запроса
        :param item: элемент запроса
        :return: объект
        """
        ow = OrderWrapper(item.pop('order_id'))
        try:
            ow.object_.weight = str(item.pop('weight'))
            ow.object_.region = item.pop('region')
            ow.delivery_hours = models.Interval.from_string_list(
                item.pop('delivery_hours'), order_fk=ow.object_
            )
            ow.clean()
        except (KeyError, ValidationError) as e:
            raise ObjectValidationError(
                ow.object_.id, str(e)) from e

        if len(ow.delivery_hours) == 0:
            raise ObjectValidationError(
                ow.object_.id, 'Empty "delivery_hours" provided'
            )

        if len(item) > 0:
            raise ObjectValidationError(
                ow.object_.id, 'Unsupported properties provided'
            )

        return ow

    @staticmethod
    def _save_object(object_):
        """
        Запись объекта в БД
        :param object_: объект для записи
        :return int: идентификатор сохраненного объекта
        """
        object_.save()
        return object_.object_.id
