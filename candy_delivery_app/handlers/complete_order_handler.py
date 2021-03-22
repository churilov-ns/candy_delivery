from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from ._request_handler import RequestWithContentHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'CompleteOrderHandler',
]


# =====================================================================================================================


class CompleteOrderHandler(RequestWithContentHandler):
    """
    Класс обработки запроса на завершение заказа
    """

    def _process(self, data):
        """
        Обработка запроса (специфическая часть)
        :param data: данные запроса
        """
        try:
            order = models.Order.objects.get(id=data['order_id'])
            courier = models.Courier.objects.get(id=data['courier_id'])
        except ObjectDoesNotExist:
            self._response = HttpResponseBadRequest
            return

        if order.courier != courier:
            self._response = HttpResponseBadRequest
        else:
            order.complete_time = data['complete_time']
            order.save()
            self._status = 200
            self._content = {
                'order_id': order.id,
            }
