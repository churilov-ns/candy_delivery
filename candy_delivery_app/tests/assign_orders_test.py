import json
from pyrfc3339 import generate
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
    FIXME: важна ли сортировка?
    FIXME: предпочитать заказ с большим весом при прочих равных?
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

    def _post_assign(self, courier_id, compare_content=True):
        """
        Отправка запроса на сревер
        """
        if courier_id is None:
            data = json.dumps({})
        else:
            data = json.dumps({'courier_id': courier_id})
        response1 = self.client.post(
            '/orders/assign', data, 'application/json')
        response2 = self.client.post(
            '/orders/assign', data, 'application/json')
        self.assertEqual(
            response1.status_code, response2.status_code)
        if compare_content:
            self.assertEqual(response1.content, response2.content)
        return response1

    def test_bad_request(self):
        """
        Назначение несуществующему курьеру
        """
        response = self._post_assign(100500, False)
        self.assertEqual(response.status_code, 400)

        response = self._post_assign(None, False)
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

    def test_assign_by_regions(self):
        """
        Назначение по районам
        """
        Order.objects.create(id=1, weight=Decimal('0.01'), region=1)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=1)
        Order.objects.create(id=2, weight=Decimal('0.01'), region=2)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=2)
        Order.objects.create(id=3, weight=Decimal('0.01'), region=4)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=3)

        response = self._post_assign(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 1},
                {'id': 2},
            ]
        )

        response = self._post_assign(2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 3},
            ]
        )

        response = self._post_assign(3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], []
        )

    def test_assign_by_working_hours(self):
        """
        Назначение по рабочим часам
        """
        Order.objects.create(id=1, weight=Decimal('0.01'), region=3)
        Interval.objects.create(min_time='09:00', max_time='10:00', order_id=1)  # -> 1
        Order.objects.create(id=2, weight=Decimal('0.01'), region=3)
        Interval.objects.create(min_time='08:00', max_time='09:01', order_id=2)  # -> 1
        Order.objects.create(id=3, weight=Decimal('0.01'), region=3)
        Interval.objects.create(min_time='09:59', max_time='10:30', order_id=3)  # -> 1
        Order.objects.create(id=4, weight=Decimal('0.01'), region=3)
        Interval.objects.create(min_time='10:00', max_time='12:01', order_id=4)  # -> 2
        Order.objects.create(id=5, weight=Decimal('0.01'), region=3)
        Interval.objects.create(min_time='08:00', max_time='09:00', order_id=5)  # -> 3

        response = self._post_assign(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 1},
                {'id': 2},
                {'id': 3},
            ]
        )

        response = self._post_assign(2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 4},
            ]
        )

        response = self._post_assign(3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 5},
            ]
        )

    def test_assign_by_weight(self):
        """
        Назначение по весу
        """
        Order.objects.create(id=1, weight=Decimal('5'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=1)  # -> 1
        Order.objects.create(id=2, weight=Decimal('4.51'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=2)  # -> 1
        Order.objects.create(id=3, weight=Decimal('0.49'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=3)  # -> 1
        Order.objects.create(id=4, weight=Decimal('8.01'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=4)  # -> 2
        Order.objects.create(id=5, weight=Decimal('6.98'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=5)  # -> 2
        Order.objects.create(id=6, weight=Decimal('30.55'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=6)  # -> x
        Order.objects.create(id=7, weight=Decimal('25.15'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=7)  # -> 3

        response = self._post_assign(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 3},
                {'id': 2},
                {'id': 1},
            ]
        )

        response = self._post_assign(2)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 5},
                {'id': 4},
            ]
        )

        response = self._post_assign(3)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content)['orders'], [
                {'id': 7},
            ]
        )

    def test_assign_with_incomplete_delivery(self):
        """
        Назначение при незавершенном заказе
        """
        Order.objects.create(id=1, weight=Decimal('5'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=1)  # -> 1
        Order.objects.create(id=2, weight=Decimal('4.51'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=2)  # -> 1
        Order.objects.create(id=3, weight=Decimal('0.49'), region=3)
        Interval.objects.create(min_time='00:00', max_time='23:59', order_id=3)  # -> 1

        delivery = Delivery.objects.create(
            courier_id=1, earnings_factor=1)
        delivery.order_set.create(id=4, weight=Decimal('1'), region=1,
                                  complete_time=delivery.assign_time)
        delivery.order_set.create(id=5, weight=Decimal('1'), region=1)
        delivery.order_set.create(id=6, weight=Decimal('1'), region=1)

        response = self._post_assign(1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'orders': [{'id': 5}, {'id': 6}],
                'assign_time': generate(
                    delivery.assign_time, utc=False, microseconds=True
                ),
            }
        )
