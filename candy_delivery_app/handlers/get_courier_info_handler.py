from django.db.models import Q
from django.http import HttpResponseBadRequest
from ._courier_handler import CourierHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'GetCourierInfoHandler',
]


# =====================================================================================================================


class Assignment(object):
    """
    Развоз
    """

    def __init__(self, first_order):
        self.__orders = [first_order]

    @property
    def orders(self):
        return self.__orders

    @property
    def assign_time(self):
        return self.__orders[0].assign_time

    @property
    def is_complete(self):
        for order in self.__orders:
            if order.complete_time is None:
                return False
        return True


class AssignmentManager(object):
    """
    Развоз
    """

    def __init__(self, courier):
        self.assignments = dict()
        assigned_orders = models.Order.objects.filter(
            courier=courier).order_by('assign_time', 'complete_time')
        for order in assigned_orders:
            try:
                self.assignments[order.assign_time].orders.append(order)
            except KeyError:
                self.assignments[order.assign_time] = Assignment(order)


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

        # Прочитать заказы, выполненные данным курьером,
        # сгруппированные по развозам
        # complete_assignments =

        # Рейтинг
        # ...
        # ...

        # Заработок
        # ...
        # ...
