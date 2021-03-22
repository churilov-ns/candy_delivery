from contextlib import suppress
from django.http import HttpResponseBadRequest
from django.core.exceptions import ValidationError
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
                courier_wrapper.type = models.CourierType(
                    type=data.pop('courier_type'), courier=courier_wrapper.object_
                )
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

        assigned_orders = courier_wrapper.object_.order_set.filter(
            complete_time=None).order_by('-weight')
        total_weight = sum([o.weight for o in assigned_orders])
        for order in assigned_orders:
            if not courier_wrapper.test_order(OrderWrapper(order, True)) or \
                    not courier_wrapper.test_weight(total_weight):
                total_weight -= order.weight
                order.courier = None
                order.assign_time = None
                order.save()

        self._status = 200
        self._content = courier_wrapper.to_json_data()
