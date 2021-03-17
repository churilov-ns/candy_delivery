import json
import time
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from . import models


# =====================================================================================================================


@require_POST
def post_couriers(request):
    """
    Загрузка списка курьеров в систему
    """
    data = json.loads(request.read())
    created_couriers = list()
    for item in data['data']:
        courier = models.Courier()
        courier.id = item['courier_id']
        courier.type = item['courier_type']
        courier.save()

        for code in item['regions']:
            region = models.Region()
            region.courier = courier
            region.code = code
            region.save()

        for interval_str in item['working_hours']:
            interval = models.Interval()
            interval.courier = courier
            interval.start, interval.end = interval_str.split('-')
            interval.save()

        created_couriers.append({'id': courier.id})

    return JsonResponse({'couriers': created_couriers})
