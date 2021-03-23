import json
from decimal import Decimal
from django.test import TestCase
from ..models import *


# =====================================================================================================================


__all__ = [
    'AssignOrdersTest',
]


# =====================================================================================================================


class AssignOrdersTest(TestCase):
    """
    Тесты назначения заказов курьерам
    """

    # Отключить ограничение на вывод
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Инициализация тестовых данных
        """
        # Курьер 1
        Courier.objects.create(id=1, type='foot')
        Region.objects.create(number=1, courier_id=1)
        Region.objects.create(number=2, courier_id=1)
        Region.objects.create(number=3, courier_id=1)
        Interval.objects.create(min_time='09:00', max_time='10:00', courier_id=1)

        # Курьер 2
        Courier.objects.create(id=2, type='bike')
        Region.objects.create(number=3, courier_id=2)
        Region.objects.create(number=4, courier_id=2)
        Interval.objects.create(min_time='09:00', max_time='10:00', courier_id=2)
        Interval.objects.create(min_time='12:00', max_time='18:00', courier_id=2)

        # Курьер 3
        Courier.objects.create(id=3, type='car')
        Region.objects.create(number=3, courier_id=3)
        Region.objects.create(number=5, courier_id=3)
        Region.objects.create(number=6, courier_id=3)
        Region.objects.create(number=7, courier_id=3)
        Region.objects.create(number=8, courier_id=3)
        Interval.objects.create(min_time='08:00', max_time='11:00', courier_id=3)
        Interval.objects.create(min_time='11:30', max_time='16:45', courier_id=3)
        Interval.objects.create(min_time='19:00', max_time='23:00', courier_id=3)

    def _post_assign(self, courier_id):
        """
        Отправка запроса на сревер
        """
        return self.client.post(
            '/orders/assign',
            json.dumps({'courier_id': courier_id}),
            'application/json'
        )

    def test_bad_request(self):
        """
        Назначение несуществующему курьеру
        """
        response = self._post_assign(100500)
        self.assertEqual(response.status_code, 400)

    def test_empty_orders(self):
        """
        Нет подходящих заказов
        """
        Order.objects.create(id=1, weight=Decimal('0.01'), region=100)
        Interval.objects.create(min_time='09:00', max_time='11:00', order_id=1)

        response = self._post_assign(1)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, '{"orders": []}')


