from ._request_handler import RequestHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportCouriersHandler',
]


# =====================================================================================================================


class ImportCouriersHandler(RequestHandler):
    """
    Обработчик запроса на добавление курьеров
    """

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process(self, data):
        couriers = list()
        invalid_ids = list()
        try:
            for item in data['data']:
                try:
                    courier = models.Courier.create_from_item(item)
                    courier.full_clean()
                    couriers.append(courier)
                except models.ObjectValidationError as e:
                    invalid_ids.append(e.object_id)
        except (KeyError, TypeError) as e:
            self._status = 400
            self._content = {
                'error': e.__str__()
            }
            return

        if len(invalid_ids) > 0:
            self._status = 400
            self._content = {
                'validation_error': {
                    'couriers': self.__create_ids_list(invalid_ids),
                },
            }
        else:
            imported_ids = list()
            for courier in couriers:
                courier.save()
                courier.save_related_objects()
                imported_ids.append(courier.id)
            self._status = 201
            self._content = {
                'couriers': self.__create_ids_list(imported_ids),
            }

    @staticmethod
    def __create_ids_list(ids):
        return [{'id': i} for i in ids]
