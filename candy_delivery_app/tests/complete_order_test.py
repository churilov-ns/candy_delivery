import pytz
import json
from datetime import datetime
from django.test import TestCase
from ..models import *


# =====================================================================================================================


__all__ = [
    'CompleteOrderTest',
]


# =====================================================================================================================


class CompleteOrderTest(TestCase):
    """
    Тесты завершения заказа
    TODO: проверка наличия courier_id в запросе
    TODO: проверка наличия order_id в запросе
    TODO: валидация complete_time (формат, assign_time)
    TODO: проверить завершить уже завершенный заказ
    """

    # Отключить ограничение на вывод
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Инициализация тестовых данных
        """
        courier = Courier.objects.create(id=1, type='foot')
        cls.delivery1 = Delivery.objects.create(
            courier=courier, earnings_factor=courier.earnings_factor)
        Order.objects.create(id=1, weight=Decimal('1'), region=1, delivery=cls.delivery1)
        Order.objects.create(id=2, weight=Decimal('1'), region=1, delivery=cls.delivery1)
        Order.objects.create(id=3, weight=Decimal('1'), region=1, delivery=cls.delivery1)

        courier = Courier.objects.create(id=2, type='foot')
        cls.delivery2 = Delivery.objects.create(
            courier=courier, earnings_factor=courier.earnings_factor)
        Order.objects.create(id=4, weight=Decimal('1'), region=1, delivery=cls.delivery2)
        Order.objects.create(id=5, weight=Decimal('1'), region=1, delivery=cls.delivery2)

        Order.objects.create(id=6, weight=Decimal('1'), region=1)

    def __post_complete(self, courier_id, order_id):
        """
        Отправка запроса на зевершение заказа
        """
        complete_time = pytz.timezone(
            "Europe/Paris").localize(datetime.now())
        data = json.dumps({
            'courier_id': courier_id,
            'order_id': order_id,
            'complete_time': str(complete_time),
        })
        return self.client.post(
            '/orders/complete', data, 'application/json'
        )

    def test_invalid_requests(self):
        """
        Проверка на ошибочных запросах
        """
        response = self.__post_complete(1, 4)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(1, 6)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(2, 1)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(100500, 1)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(100500, 100500)
        self.assertEqual(response.status_code, 400)

    def test_valid_requests(self):
        """
        Проверка на корректных запросах
        """
        response = self.__post_complete(1, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 1,
            }
        )
        CompleteOrderTest.delivery1.refresh_from_db()
        self.assert_(not CompleteOrderTest.delivery1.is_complete)

        response = self.__post_complete(2, 4)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 4,
            }
        )
        CompleteOrderTest.delivery2.refresh_from_db()
        self.assert_(not CompleteOrderTest.delivery2.is_complete)

        response = self.__post_complete(1, 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 2,
            }
        )
        CompleteOrderTest.delivery1.refresh_from_db()
        self.assert_(not CompleteOrderTest.delivery1.is_complete)

        response = self.__post_complete(1, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 3,
            }
        )
        CompleteOrderTest.delivery1.refresh_from_db()
        self.assert_(CompleteOrderTest.delivery1.is_complete)

        response = self.__post_complete(2, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 5,
            }
        )
        CompleteOrderTest.delivery2.refresh_from_db()
        self.assert_(CompleteOrderTest.delivery2.is_complete)
