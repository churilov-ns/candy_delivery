from ._import_handler import ImportHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportCouriersHandler',
]


# =====================================================================================================================


class ImportCouriersHandler(ImportHandler):
    """
    Обработчик запроса на добавление курьеров
    """

    _OUTPUT_KEY = 'couriers'

    @staticmethod
    def _init_object(item):
        return models.Courier.from_item(item)

    @staticmethod
    def _save_object(object_):
        object_.save()
        object_.save_related_objects()
