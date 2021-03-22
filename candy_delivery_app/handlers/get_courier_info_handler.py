from ._courier_handler import CourierHandler
from ._request_handler import RequestWithContentHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'GetCourierInfoHandler',
]


# =====================================================================================================================


class GetCourierInfoHandler(RequestWithContentHandler, CourierHandler):
    """
    Обработчик запроса на получение данных о курьере
    """

    def _process_courier(self, courier_wrapper, data):
        """
        Обработка запроса (специфическая часть)
        :param CourierWrapper courier_wrapper: данные по курьеру
        :param data: данные запроса
        """
        # Основные данные
        self._status = 200
        self._content = courier_wrapper.to_json_data()

        # Заработок
        self._content['earnings'] = sum([
            d.earnings_factor * 500
            for d in courier_wrapper.object_.delivery_set.filter(
                is_complete=True
            )
        ])

        # Рейтинг
        rating = 0.0
        # ...
        # ...
