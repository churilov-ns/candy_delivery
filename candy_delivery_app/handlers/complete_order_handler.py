from pyrfc3339 import parse
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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
            courier_id = CompleteOrderHandler._test_type(
                data['courier_id'], {int})
            order_id = CompleteOrderHandler._test_type(
                data['order_id'], {int})
            complete_time = CompleteOrderHandler._test_type(
                data['complete_time'], {str})

            complete_time = parse(complete_time)
            order = models.Order.objects.get(id=order_id)
        except (KeyError, ValueError, ObjectDoesNotExist, ValidationError):
            self._response = HttpResponseBadRequest()
            return

        if order.delivery is None \
                or order.delivery.courier.id != courier_id \
                or order.delivery.assign_time > complete_time:
            self._response = HttpResponseBadRequest()
            return

        try:
            start_time = order.delivery.order_set.exclude(
                complete_time=None
            ).latest('complete_time').complete_time
        except ObjectDoesNotExist:
            start_time = order.delivery.assign_time

        order.complete_time = complete_time
        order.delivery_duration = (order.complete_time - start_time)\
            .total_seconds()
        order.save()
        order.delivery.update_complete()

        if order.delivery_duration <= 0:
            self.__recalculate_duration(order.delivery)

        self._status = 200
        self._content = {
            'order_id': order.id,
        }

    @staticmethod
    def __recalculate_duration(delivery):
        """
        Пересчет продолжительсноти доставки заказов в развозе
        :param models.Delivery delivery: развоз
        """
        start_time = delivery.assign_time
        orders = delivery.order_set.exclude(
                complete_time=None
            ).order_by('complete_time')
        for order in orders:
            order.delivery_duration = (
                    order.complete_time - start_time
            ).total_seconds()
            order.save()
            start_time = order.complete_time
