import json
from datetime import timedelta
from django.test import TestCase
from ..models import *


# =====================================================================================================================

__all__ = [
    'GetCourierInfoTest',
]


# =====================================================================================================================


class GetCourierInfoTest(TestCase):
    """
    Тест получения статистики курьера
    """

    # Отключить ограничение на вывод
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        """
        Инициализация тестовых данных
        """
        cls.courier = Courier.objects.create(id=1, type='foot')
        cls.courier.region_set.create(number=1)
        cls.courier.region_set.create(number=2)
        cls.courier.region_set.create(number=3)
        cls.courier.interval_set.create(min_time='12:00', max_time='13:00')
        cls.courier.interval_set.create(min_time='18:00', max_time='19:00')

    def __get_info(self, courier_id):
        """
        Отправка запроса на сревер
        """
        return self.client.get(
            '/couriers/{0}'.format(courier_id)
        )

    def __post_complete(self, courier_id, order_id, complete_time):
        """
        Завершение заказа
        """
        self.client.post('/orders/complete', json.dumps({
            'courier_id': courier_id,
            'order_id': order_id,
            'complete_time': complete_time.isoformat(),
        }), 'application/json')

    def test_invalid_courier(self):
        """
        Тест несуществующего курьера
        """
        response = self.__get_info(100500)
        self.assertEqual(response.status_code, 404)

    def test_courier_without_orders(self):
        """
        Тест на курьере без заказов
        """
        response = self.__get_info(GetCourierInfoTest.courier.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['12:00-13:00', '18:00-19:00'],
                'earnings': 0,
            }
        )

    def test_courier_with_incomplete_delivery(self):
        """
        Тест на курьере с незавершенным развозом
        """
        delivery = GetCourierInfoTest.courier.delivery_set.create(
            earnings_factor=GetCourierInfoTest.courier.earnings_factor)
        delivery.order_set.create(id=1, weight=Decimal('1'), region=1)
        delivery.order_set.create(id=2, weight=Decimal('1'), region=1)
        self.__post_complete(
            GetCourierInfoTest.courier.id, 1,
            delivery.assign_time + timedelta(seconds=3600.)
        )

        response = self.__get_info(GetCourierInfoTest.courier.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['12:00-13:00', '18:00-19:00'],
                'earnings': 0,
            }
        )

    def test_courier_with_complete_deliveries(self):
        """
        Тест на курьере с завершенными развозами
        """
        # Развоз 1 (C=2)
        delivery = GetCourierInfoTest.courier.delivery_set.create(
            earnings_factor=GetCourierInfoTest.courier.earnings_factor)
        delivery.order_set.create(id=1, weight=Decimal('1'), region=1)
        delivery.order_set.create(id=2, weight=Decimal('1'), region=2)
        delivery.order_set.create(id=3, weight=Decimal('1'), region=3)
        self.__post_complete(
            GetCourierInfoTest.courier.id, 1,
            delivery.assign_time + timedelta(seconds=3600.)
        )
        self.__post_complete(
            GetCourierInfoTest.courier.id, 2,
            delivery.assign_time + timedelta(seconds=300.)
        )
        self.__post_complete(
            GetCourierInfoTest.courier.id, 3,
            delivery.assign_time + timedelta(seconds=3850.)
        )

        # Пересел в тачку
        GetCourierInfoTest.courier.type = 'car'
        GetCourierInfoTest.courier.save()

        # Развоз 2 (C=9)
        delivery = GetCourierInfoTest.courier.delivery_set.create(
            earnings_factor=GetCourierInfoTest.courier.earnings_factor)
        delivery.order_set.create(id=4, weight=Decimal('1'), region=1)
        delivery.order_set.create(id=5, weight=Decimal('1'), region=2)
        self.__post_complete(
            GetCourierInfoTest.courier.id, 4,
            delivery.assign_time + timedelta(seconds=900.)
        )
        self.__post_complete(
            GetCourierInfoTest.courier.id, 5,
            delivery.assign_time + timedelta(seconds=1800.)
        )

        # Развоз 3 (C=9) - не завершен
        delivery = GetCourierInfoTest.courier.delivery_set.create(
            earnings_factor=GetCourierInfoTest.courier.earnings_factor)
        delivery.order_set.create(id=6, weight=Decimal('1'), region=3)
        delivery.order_set.create(id=7, weight=Decimal('1'), region=1)
        self.__post_complete(
            GetCourierInfoTest.courier.id, 6,
            delivery.assign_time + timedelta(seconds=2300.)
        )

        # Запрос данных
        response = self.__get_info(GetCourierInfoTest.courier.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            json.loads(response.content), {
                'courier_id': 1,
                'courier_type': 'car',
                'regions': [1, 2, 3],
                'working_hours': ['12:00-13:00', '18:00-19:00'],
                'rating': 16750./3600.,  # сложно
                'earnings': 5500,  # 2*500 + 9*500
            }
        )
