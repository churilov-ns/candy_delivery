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

    def __post_complete(self, courier_id, order_id, content_expected=True):
        """
        Отправка запроса на зевершение заказа
        """
        tz = pytz.timezone("Europe/Moscow")
        complete_time = datetime.now().astimezone(tz)
        data = {'complete_time': complete_time.isoformat()}
        if courier_id is not None:
            data['courier_id'] = courier_id
        if order_id is not None:
            data['order_id'] = order_id

        data = json.dumps(data)
        result1 = self.client.post(
            '/orders/complete', data, 'application/json'
        )
        result2 = self.client.post(
            '/orders/complete', data, 'application/json'
        )
        self.assertEqual(
            result1.status_code, result2.status_code
        )
        if content_expected:
            self.assertEqual(
                result1.content, result2.content
            )
        return result1

    def test_invalid_requests(self):
        """
        Проверка на ошибочных запросах
        """
        response = self.__post_complete(1, 4, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(1, 6, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(2, 1, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(100500, 1, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(100500, 100500, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(None, 1, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete(1, None, False)
        self.assertEqual(response.status_code, 400)

        response = self.__post_complete('1', '1', False)
        self.assertEqual(response.status_code, 400)

    def test_valid_requests(self):
        """
        Проверка на корректных запросах
        """
        d1 = CompleteOrderTest.delivery1
        d2 = CompleteOrderTest.delivery2

        response = self.__post_complete(1, 1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 1,
            }
        )
        d1.refresh_from_db()
        self.assert_(not d1.is_complete)
        o1 = d1.order_set.get(id=1)
        self.assertEqual(
            (o1.complete_time - d1.assign_time).total_seconds(),
            o1.delivery_duration
        )

        response = self.__post_complete(2, 4)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 4,
            }
        )
        d2.refresh_from_db()
        self.assert_(not d2.is_complete)
        o4 = d2.order_set.get(id=4)
        self.assertEqual(
            (o4.complete_time - d2.assign_time).total_seconds(),
            o4.delivery_duration
        )

        response = self.__post_complete(1, 2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 2,
            }
        )
        d1.refresh_from_db()
        self.assert_(not d1.is_complete)
        o2 = d1.order_set.get(id=2)
        self.assertEqual(
            (o2.complete_time - o1.complete_time).total_seconds(),
            o2.delivery_duration
        )

        response = self.__post_complete(1, 3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 3,
            }
        )
        d1.refresh_from_db()
        self.assert_(d1.is_complete)
        o3 = d1.order_set.get(id=3)
        self.assertEqual(
            (o3.complete_time - o2.complete_time).total_seconds(),
            o3.delivery_duration
        )

        response = self.__post_complete(2, 5)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'order_id': 5,
            }
        )
        d2.refresh_from_db()
        self.assert_(d2.is_complete)
        o5 = d2.order_set.get(id=5)
        self.assertEqual(
            (o5.complete_time - o4.complete_time).total_seconds(),
            o5.delivery_duration
        )
