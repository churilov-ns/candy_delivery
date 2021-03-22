import abc
import json
from django.http import JsonResponse


# =====================================================================================================================


__all__ = [
    'RequestHandler',
    'RequestWithContentHandler',
    'RequestWithoutContentHandler',
]


# =====================================================================================================================


class RequestHandler(abc.ABC):
    """
    Базовый класс обработки запроса
    """

    def __init__(self, parse_request_content, *, default_status=500):
        """
        Инициализация
        :param bool parse_request_content: флаг разбора содержимого запроса
        :param int default_status: статус ответа по умолчанию
        """
        self._parse_request_content = parse_request_content
        self._response_type = JsonResponse
        self._status = default_status
        self._content = dict()
        self._request = None
        self._response = None

    def process(self, request):
        """
        Обработка запроса
        :param request: объект запроса
        :return: результат обработки
        """
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
        """
        Обработка запроса (специфическая часть)
        :param data: данные запроса
        """
        pass

    def _create_response(self):
        """
        Формирование ответа
        :return: результат обработки
        """
        if self._response is None:
            return self._response_type(
                self._content, status=self._status
            )
        else:
            return self._response


# =====================================================================================================================


class RequestWithContentHandler(RequestHandler, abc.ABC):
    """
    Класс обработки запроса с содержимым
    """

    def __init__(self, **kwargs):
        """
        Инициализация
        :param kwargs: параметры роительского класса
        """
        super().__init__(True, **kwargs)


# =====================================================================================================================


class RequestWithoutContentHandler(RequestHandler, abc.ABC):
    """
    Класс обработки запроса без содержимого
    """

    def __init__(self, **kwargs):
        """
        Инициализация
        :param kwargs: параметры роительского класса
        """
        super().__init__(False, **kwargs)
