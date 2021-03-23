from django.test import TestCase
from ..models import *


# =====================================================================================================================


__all__ = [
    'CompleteOrderTest',
]


# =====================================================================================================================


class CompleteOrderTest(TestCase):
    """
    Тесты зершения заказа
    TODO: проверка наличия courier_id в запросе
    TODO: проверка наличия order_id в запросе
    TODO: валидация complete_time
    """

    # Отключить ограничение на вывод
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Инициализация тестовых данных
        """
        pass
