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

    def __init__(self, parse_request_content, *, default_status=500):
        self._parse_request_content = parse_request_content
        self._response_type = JsonResponse
        self._status = default_status
        self._content = dict()
        self._request = None
        self._response = None

    def process(self, request):
        self._request = request
        try:
            data = None
            if self._parse_request_content:
                data = json.loads(request.read())
            self._process(data)
        except Exception as error:
            self._status = 500
            self._content = {
                'error': str(error),
            }
        return self._create_response()

    @abc.abstractmethod
    def _process(self, data):
        pass

    def _create_response(self):
        if self._response is None:
            return self._response_type(
                self._content, status=self._status
            )
        else:
            return self._response
