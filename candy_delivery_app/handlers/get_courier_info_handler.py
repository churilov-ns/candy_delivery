from django.db.models import Sum, Avg, Min
from ._courier_handler import CourierHandler
from ._request_handler import RequestWithoutContentHandler


# =====================================================================================================================


__all__ = [
    'GetCourierInfoHandler',
]


# =====================================================================================================================


class GetCourierInfoHandler(RequestWithoutContentHandler, CourierHandler):
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

        # Заработок и рейтинг
        q = courier_wrapper.object_.delivery_set.filter(
            is_complete=True)
        if len(q) == 0:
            self._content['earnings'] = 0
        else:
            self._content['earnings'] = q.aggregate(
                Sum('earnings_factor'))['earnings_factor__sum'] * 500
            t = q.values(
                'order__region',
                avg_duration=Avg('order__delivery_duration')
            ).aggregate(Min('avg_duration'))['avg_duration__min']
            self._content['rating'] = 5. * (3600. - min(t, 3600.)) / 3600.
