from django.http import HttpResponseBadRequest
from ._courier_handler import CourierHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'UpdateCourierHandler',
]


# =====================================================================================================================


class UpdateCourierHandler(CourierHandler):
    """
    Обработчик запроса на изменение данных курьера
    """

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process_courier(self, courier, data):
        try:
            affected_fields = courier.update_from_item(data)
            courier.full_clean()
        except models.ObjectValidationError:
            self._response = HttpResponseBadRequest()
            return

        if 'regions' in affected_fields:
            courier.region_set.all().delete()
        if 'working_hours' in affected_fields:
            courier.interval_set.all().delete()
        if 'courier_type' in affected_fields:
            courier.save()
        if len(courier.related_objects) > 0:
            courier.save_related_objects()
        courier.refresh_from_db()

        # TODO: обновить назначенные заказы
        # ...
        # ...

        self._status = 200
        self._content = courier.to_item()
