from django.db.models import Q
from django.http import HttpResponseBadRequest
from ._courier_handler import CourierHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'GetCourierInfoHandler',
]


# =====================================================================================================================


class GetCourierInfoHandler(CourierHandler):
    """
    Обработчик запроса на получение данных о курьере
    """

    def __init__(self, **kwargs):
        super().__init__(False, **kwargs)

    def _process_courier(self, courier, data):
        # Основные данные
        self._status = 200
        self._content = courier.to_item()  # TODO: переименовать

        # Рейтинг
        # ...
        # ...

        # Заработок
        # ...
        # ...
