import abc
from django.http import HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from ._request_handler import RequestHandler
from ..wrappers import CourierWrapper


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
        """
        Обработка запроса (специфическая часть)
        :param data: данные запроса
        """
        try:
            courier_id = int(self._request.path.split('/')[-1])
            self._process_courier(CourierWrapper.select(courier_id), data)
        except ObjectDoesNotExist:
            self._response = HttpResponseNotFound()

    @abc.abstractmethod
    def _process_courier(self, courier_wrapper, data):
        """
        Обработка запроса (специфическая часть)
        :param CourierWrapper courier_wrapper: данные по курьеру
        :param data: данные запроса
        """
        pass
