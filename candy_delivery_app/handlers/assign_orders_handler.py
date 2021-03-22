from decimal import Decimal
from datetime import datetime
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
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
            cw = CourierWrapper.select(data['courier_id'], True)
        except ObjectDoesNotExist:
            self._response = HttpResponseBadRequest
            return

        assigned_orders = cw.object_.order_set.filter(
            complete_time=None)

        if len(assigned_orders) == 0:
            assigned_orders = list()
            assign_time = datetime.now()
            total_weight = Decimal('0.00')
            for order in models.Order.objects.firter(
                    courier=None).order_by('weight'):

                if not cw.test_order(OrderWrapper(order, True)):
                    continue

                total_weight += order.weight
                if not cw.test_weight(total_weight):
                    break

                order.assign_time = assign_time
                order.courier = cw.object_
                order.save()
                assigned_orders.append(order)

        self._status = 200
        self._content = self.__create_content(
            assigned_orders
        )

    @staticmethod
    def __create_content(assigned_orders):
        """
        Формирование выходной структуры данных
        :param list(models.Order) assigned_orders: список заказов
        :return dict: выходная структура данных
        """
        if len(assigned_orders) > 0:
            return {
                'orders': [{'id': o.id} for o in assigned_orders],
                'assign_time': assigned_orders[0].assign_time,
            }
        else:
            return {
                'orders': list()
            }
