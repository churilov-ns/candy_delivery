import abc
from django.http import HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from ._request_handler import RequestHandler
from candy_delivery_app.models import Courier


# =====================================================================================================================


__all__ = [
    'CourierHandler',
]


# =====================================================================================================================


class CourierHandler(RequestHandler, abc.ABC):
    """
    Обработчик запроса для конкретного курьера
    """

    def _process(self, data):
        try:
            courier_id = int(self._request.path.split('/')[-1])
            self._process_courier(Courier.objects.get(id=courier_id), data)
        except ObjectDoesNotExist:
            self._response = HttpResponseNotFound()

    @abc.abstractmethod
    def _process_courier(self, courier, data):
        pass
