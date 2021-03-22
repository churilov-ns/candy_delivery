from django.db.models import Q
from django.http import HttpResponseBadRequest
from ._courier_handler import CourierHandler
from .. import models


# =====================================================================================================================


__all__ = [
    'UpdateCourierHandler',
]


# =====================================================================================================================


class UpdateCourierHandler(CourierHandler):
    """
    Обработчик запроса на изменение данных курьера
    """

    def __init__(self, **kwargs):
        super().__init__(True, **kwargs)

    def _process_courier(self, courier, data):
        try:
            affected_fields = courier.update(data)  # TODO: переименовать
            courier.full_clean()
        except models.ObjectValidationError:
            self._response = HttpResponseBadRequest()
            return

        if 'regions' in affected_fields:
            courier.region_set.all().delete()
        if 'working_hours' in affected_fields:
            courier.interval_set.all().delete()
        if 'courier_type' in affected_fields:
            # TODO: сохранить историю типов
            courier.save()
        if len(courier.related_objects) > 0:
            courier.save_related_objects()
        courier.refresh_from_db()

        # TODO: обновить назначенные заказы
        if len(affected_fields) > 0:
            assigned_orders = models.Order.objects.firter(
                Q(courier=courier) & Q(complete_datetime=None)
            ).order_by('-weight')
            regions = set(courier.region_set.all())
            working_hours = courier.interval_set.all()
            total_weight = sum([o.weight for o in assigned_orders])
            for order in assigned_orders:
                drop_order = True
                for delivery_interval in order.interval_set.all():
                    for working_interval in working_hours:
                        if working_interval.intersects_with(delivery_interval):
                            drop_order = False
                            break
                if not drop_order:
                    if order.region not in regions or \
                            total_weight > courier.max_weight:
                        drop_order = True

                if drop_order:
                    total_weight -= order.weight
                    order.courier = None
                    order.assign_datetime = None
                    order.save()

        self._status = 200
        self._content = courier.to_item()
