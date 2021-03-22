from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from ._request_handler import RequestHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'CompleteOrderHandler',
]


# =====================================================================================================================


class CompleteOrderHandler(RequestHandler):
    """
    Класс обработки запроса на завершение заказа
    """

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process(self, data):
        courier_id = data['courier_id']
        order_id = data['order_id']
        complete_time = data['complete_time']

        try:
            courier = models.Courier.objects.get(id=courier_id)
            order = models.Order.objects.get(id=order_id)
        except ObjectDoesNotExist:
            self._response = HttpResponseBadRequest
            return

        if order.courier != courier:
            self._response = HttpResponseBadRequest
        else:
            order.complete_time = complete_time  # TODO: datetime -> time
            order.save()
            self._status = 200
            self._content = {
                'order_id': order_id,
            }
