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
        except ObjectDoesNotExist:
            self._response = HttpResponseBadRequest
            return

        if order.delivery is None or \
                order.delivery.courier.id != data['courier_id']:
            self._response = HttpResponseBadRequest
        else:
            try:
                start_time = order.delivery.order_set.exclude(
                    complete_time=None
                ).latest('complete_time').complete_time
            except ObjectDoesNotExist:
                start_time = order.delivery.assign_time

            order.complete_time = data['complete_time']
            order.delivery_duration = (order.complete_time - start_time)\
                .total_seconds()
            order.save()
            order.delivery.update_complete()

            self._status = 200
            self._content = {
                'order_id': order.id,
            }
