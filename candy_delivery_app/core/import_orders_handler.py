from ._import_handler import ImportHandler
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

    _OUTPUT_KEY = 'orders'

    @staticmethod
    def _init_object(item):
        return models.Order.from_item(item)

    @staticmethod
    def _save_object(object_):
        object_.save()
        object_.save_related_objects()
