import pyrfc3339
from decimal import Decimal
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ._request_handler import RequestWithContentHandler
from ..wrappers import CourierWrapper, OrderWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'AssignOrdersHandler',
]


# =====================================================================================================================


class AssignOrdersHandler(RequestWithContentHandler):
    """
    Класс обработки запроса на назначение заказов курьеру
    """

    def _process(self, data):
        """
        Обработка запроса (специфическая часть)
        :param data: данные запроса
        """
        try:
            courier_id = AssignOrdersHandler._test_type(
                data['courier_id'], {int})
            cw = CourierWrapper.select(courier_id, True)
        except (KeyError, ValidationError, ObjectDoesNotExist):
            self._response = HttpResponseBadRequest()
            return

        try:
            delivery = models.Delivery.objects.get(
                courier=cw.object_, is_complete=False
            )
        except ObjectDoesNotExist:
            delivery = models.Delivery.objects.create(
                courier=cw.object_,
                earnings_factor=cw.object_.earnings_factor
            )

            total_weight = Decimal('0.00')
            free_orders = models.Order.objects.filter(
                delivery=None).order_by('weight')
            for order in free_orders:
                if not cw.test_order(OrderWrapper(order, True)):
                    continue

                total_weight += order.weight
                if total_weight > cw.object_.max_weight:
                    break

                delivery.order_set.add(order)

        self._status = 200
        self._content = self.__create_content(
            delivery
        )

    @staticmethod
    def __create_content(delivery):
        """
        Формирование выходной структуры данных
        :param models.Delivery delivery: развоз
        :return dict: выходная структура данных
        """
        orders = delivery.order_set.all()
        if len(orders) > 0:
            return {
                'orders': [
                    {'id': o.id} for o in orders if o.complete_time is None
                ],
                'assign_time': pyrfc3339.generate(
                    delivery.assign_time, utc=False, microseconds=True
                ),
            }
        else:
            delivery.delete()
            return {
                'orders': list()
            }
