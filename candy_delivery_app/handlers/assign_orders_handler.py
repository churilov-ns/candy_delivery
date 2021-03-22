from decimal import Decimal
from datetime import datetime
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from ._request_handler import RequestHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'AssignOrdersHandler',
]


# =====================================================================================================================


class AssignOrdersHandler(RequestHandler):
    """
    Класс обработки запроса на назначение заказов курьеру
    """

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process(self, data):
        courier_id = data['courier_id']
        try:
            courier = models.Courier.objects.get(id=courier_id)
        except ObjectDoesNotExist:
            self._response = HttpResponseBadRequest
            return

        assigned_orders = models.Order.objects.firter(
            Q(courier=courier) & Q(complete_datetime=None))
        if len(assigned_orders) > 0:
            assign_datetime = assigned_orders[0].assign_time

        assign_datetime = datetime.now()
        regions = set(courier.region_set.all())
        working_hours = courier.interval_set.all()
        free_orders = models.Order.objects.firter(courier=None).order_by('weight')
        total_weight = Decimal('0.00')
        assigned_orders = list()
        for order in free_orders:
            if order.region not in regions:
                continue
            match = False
            for delivery_interval in order.interval_set.all():
                for working_interval in working_hours:
                    if working_interval.intersects_with(delivery_interval):
                        match = True
                        break
            if not match:
                continue
            total_weight += order.weight
            if total_weight > courier.max_weight:
                break

            order.courier = courier
            order.assign_time = assign_datetime
            order.save()

            assigned_orders.append(order)

        if len(assigned_orders) > 0:
            pass
        else:
            pass
