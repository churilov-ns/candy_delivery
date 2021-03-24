from decimal import Decimal
from contextlib import suppress
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from ._request_handler import RequestWithContentHandler
from ._courier_handler import CourierHandler
from ..wrappers import CourierWrapper, OrderWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'UpdateCourierHandler',
]


# =====================================================================================================================


class UpdateCourierHandler(RequestWithContentHandler, CourierHandler):
    """
    Обработчик запроса на изменение данных курьера
    """

    def _process_courier(self, courier_wrapper, data):
        """
        Обработка запроса (специфическая часть)
        :param CourierWrapper courier_wrapper: данные по курьеру
        :param data: данные запроса
        """
        try:
            with suppress(KeyError):
                courier_wrapper.object_.type = data.pop('courier_type')
            with suppress(KeyError):
                courier_wrapper.regions = models.Region.from_number_list(
                    data.pop('regions'), courier_wrapper.object_
                )
            with suppress(KeyError):
                courier_wrapper.working_hours = models.Interval.from_string_list(
                    data.pop('working_hours'), courier_fk=courier_wrapper.object_
                )
            courier_wrapper.clean()
        except ValidationError:
            self._response = HttpResponseBadRequest()
            return

        if len(data) > 0:
            self._response = HttpResponseBadRequest()
            return

        courier_wrapper.save(True)
        courier_wrapper.refresh()
        self._status = 200
        self._content = courier_wrapper.to_json_data()
        self.__update_current_delivery(courier_wrapper)

    @staticmethod
    def __update_current_delivery(courier_wrapper):
        """
        Обновление текущего развоза
        :param CourierWrapper courier_wrapper: данные по курьеру
        """
        # Получение текущей (незавершенной) доставки
        try:
            current_delivery = models.Delivery.objects.get(
                courier=courier_wrapper.object_, is_complete=False)
        except ObjectDoesNotExist:
            return

        # Список незавершенных заказов
        incomplete_orders = list(
            current_delivery.order_set.filter(
                complete_time=None).order_by('weight')
        )

        # Сначала выбросим все, что не подходит
        # по району и времени доставки
        temp_orders = list()
        total_weight = Decimal('0.00')
        for order in incomplete_orders:
            if courier_wrapper.test_order(
                    OrderWrapper(order, True)):
                total_weight += order.weight
                temp_orders.append(order)
            else:
                order.delivery = None
                order.save()
        incomplete_orders = temp_orders

        # Теперь выбросим заказы, не подходящие по весу
        while len(incomplete_orders) > 0 and \
                total_weight > courier_wrapper.object_.max_weight:
            order = incomplete_orders.pop()
            order.delivery = None
            order.save()
            total_weight -= order.weight

        # Если незавершенных заказов не осталось,
        # то справедливо одно из двух:
        # 1) заказов не осталось вообще - удалить доставку
        # 2) остались только завершенные заказы - завершить доставку
        if len(incomplete_orders) == 0:
            if len(current_delivery.order_set.all()) > 0:
                current_delivery.is_complete = True
                current_delivery.save()
            else:
                current_delivery.delete()
