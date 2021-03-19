from contextlib import suppress
from django.http import HttpResponseBadRequest
from ._courier_handler import CourierHandler
from candy_delivery_app.models import Region, Interval


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
        with suppress(KeyError):
            courier.type = data.pop('courier_type')

        new_regions = list()
        with suppress(KeyError):
            for region in data.pop('regions'):
                new_regions.append(Region(
                    code=region,
                    courier=courier,
                ))

        new_intervals = list()
        with suppress(KeyError):
            for interval in data.pop('working_hours'):
                parts = interval.split('-')
                new_intervals.append(Interval(
                    start=parts[0],
                    end=parts[1],
                    courier=courier,
                ))

        if len(data) > 0:
            self._response = HttpResponseBadRequest()
            return

        if len(new_regions) > 0:
            courier.region_set.all().delete()
            for region in new_regions:
                region.save()
        if len(new_intervals) > 0:
            courier.interval_set.all().delete()
            for interval in new_intervals:
                interval.save()
        courier.save()
        courier.refresh_from_db()

        self._status = 200
        self._content = {
            'courier_id': courier.id,
            'courier_type': courier.type,
            'regions': [r.code for r in courier.region_set.all()],
            'working_hours': [str(i) for i in courier.interval_set.all()],
        }
