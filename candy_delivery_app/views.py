from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .handlers import (
    ImportCouriersHandler,
    UpdateCourierHandler,
    ImportOrdersHandler,
    AssignOrdersHandler,
    CompleteOrderHandler,
)


# =====================================================================================================================


@require_POST
def post_couriers(request):
    """
    Загрузка списка курьеров в систему
    """
    return ImportCouriersHandler().process(request)


def get_patch_courier(request):
    """
    Обновление/выдача информации о курьере
    """
    if request.method == 'PATCH':
        return UpdateCourierHandler().process(request)
    elif request.method == 'GET':
        pass
    else:
        return JsonResponse(
            {'error': 'Allowed methods are: PATCH, GET'}, status=405
        )


@require_POST
def post_orders(request):
    """
    Загрузка списка заказов в систему
    """
    return ImportOrdersHandler().process(request)


@require_POST
def post_orders_assign(request):
    """
    Назначение заказов курьеру
    """
    return AssignOrdersHandler().process(request)


@require_POST
def post_orders_complete(request):
    """
    Регистрация выполнения заказа
    """
    return CompleteOrderHandler().process(request)
