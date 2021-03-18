import abc
import json
from django.http import JsonResponse


# =====================================================================================================================


__all__ = [
    'RequestHandler',
]


# =====================================================================================================================


class RequestHandler(abc.ABC):
    """
    Базовый класс обработки запроса
    """

    def __init__(self, *, default_status=500, default_reason=None):
        self._status = default_status
        self._reason = default_reason
        self._content = dict()
        self._request = None

    def process(self, request):
        try:
            self._request = request
            self._process(json.loads(request.read()))
        except Exception as error:
            self._status = 500
            self._reason = None
            self._content = {
                'error': str(error),
            }
        return self._create_response()

    @abc.abstractmethod
    def _process(self, data):
        pass

    def _create_response(self):
        return JsonResponse(self._content, status=self._status, reason=self._reason)
