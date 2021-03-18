# from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from .core import ImportCouriersHandler


# =====================================================================================================================


@require_POST
def post_couriers(request):
    """
    Загрузка списка курьеров в систему
    """
    return ImportCouriersHandler().process(request)
