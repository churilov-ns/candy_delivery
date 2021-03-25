from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from ..models import *


# =====================================================================================================================


__all__ = [
    'UpdateCourierTest',
]


# =====================================================================================================================


class UpdateCourierTest(TestCase):
    """
    Тесты на обновление данных о курьере
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
        Region.objects.create(courier_id=1, number=1)
        Region.objects.create(courier_id=1, number=12)
        Region.objects.create(courier_id=1, number=22)
        Interval.objects.create(courier_id=1, min_time='09:00', max_time='11:00')
        Interval.objects.create(courier_id=1, min_time='11:35', max_time='14:05')

        # Курьер 2
        Courier.objects.create(id=2, type='bike')
        Region.objects.create(courier_id=2, number=22)
        Interval.objects.create(courier_id=2, min_time='09:00', max_time='18:00')

        # Курьер 3
        Courier.objects.create(id=3, type='car')
        Region.objects.create(courier_id=3, number=12)
        Region.objects.create(courier_id=3, number=22)
        Region.objects.create(courier_id=3, number=23)
        Region.objects.create(courier_id=3, number=33)

    def __test_request(self, courier_id, data, expected_status, expected_content):
        """
        Тестирование одного запроса
        :param courier_id: id курьера
        :param data: данные запроса
        :param expected_status: ожидаемый статус ответа
        :param expected_content: ожидаемое содержимое ответа
        """

        response = self.client.patch(
            '/couriers/{0}'.format(courier_id), data, 'application/json')
        self.assertEqual(response.status_code, expected_status)
        if expected_content is None:
            self.assertEqual(response.content, b'')
        else:
            self.assertJSONEqual(response.content, expected_content)

    def test_valid_requests(self):
        """
        Коррекные запросы
        """

        data = \
            '{' \
            '   "courier_type": "car"' \
            '}'
        expected_content = \
            '{' \
            '   "courier_id": 1, ' \
            '   "courier_type": "car", ' \
            '   "regions": [1, 12, 22], ' \
            '   "working_hours": ["09:00-11:00", "11:35-14:05"]' \
            '}'
        self.__test_request(1, data, 200, expected_content)

        data = \
            '{' \
            '   "regions": [1, 5], ' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"]' \
            '}'
        expected_content = \
            '{' \
            '   "courier_id": 2, ' \
            '   "courier_type": "bike", ' \
            '   "regions": [1, 5], ' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"]' \
            '}'
        self.__test_request(2, data, 200, expected_content)

        data = \
            '{' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"]' \
            '}'
        expected_content = \
            '{' \
            '   "courier_id": 3, ' \
            '   "courier_type": "car", ' \
            '   "regions": [12, 22, 23, 33],' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"]' \
            '}'
        self.__test_request(3, data, 200, expected_content)

    def test_invalid_requests(self):
        """
        Некоррекные запросы
        """

        # Несуществующий курьер
        self.__test_request(100, '{}', 404, None)

        # Неизвестное поле
        data = \
            '{' \
            '   "regions": [1, 5], ' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"],' \
            '   "unknown_field": 100500' \
            '}'
        self.__test_request(1, data, 400, None)

        # Ошибки в courier_type
        data = \
            '{' \
            '   "courier_type": "airplane",' \
            '   "regions": [22],' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": null,' \
            '   "regions": [22],' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)

        # Ошибки в regions
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": 22,' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": {"number": 22},' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": [-1, 22, 32],' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": ["22", 32.154],' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)

        # Ошибки в working_hours
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": [22],' \
            '   "working_hours": ["09:00:13 - 18:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": [22],' \
            '   "working_hours": ["18:00-09:00"]' \
            '}'
        self.__test_request(1, data, 400, None)
        data = \
            '{' \
            '   "courier_type": "bike",' \
            '   "regions": [22],' \
            '   "working_hours": 12' \
            '}'
        self.__test_request(1, data, 400, None)

    def test_with_incomplete_delivery_1(self):
        """
        Тест с незавершенным заказом N1
        """
        courier = Courier.objects.get(id=2)
        delivery = Delivery.objects.create(
            courier=courier, earnings_factor=courier.earnings_factor)
        test_earnings_factor = delivery.earnings_factor
        order1 = Order.objects.create(
            id=1, weight=Decimal('0.01'), region=22, delivery=delivery,
            complete_time=delivery.assign_time)
        order2 = Order.objects.create(
            id=2, weight=Decimal('10.01'), region=22, delivery=delivery)
        order3 = Order.objects.create(
            id=3, weight=Decimal('2.45'), region=22, delivery=delivery)
        order1.interval_set.create(min_time='00:00', max_time='23:59')
        order2.interval_set.create(min_time='00:00', max_time='23:59')
        order3.interval_set.create(min_time='00:00', max_time='23:59')

        expected_content = \
            '{' \
            '   "courier_id": 2, ' \
            '   "courier_type": "foot", ' \
            '   "regions": [22], ' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(2, '{"courier_type": "foot"}', 200, expected_content)

        order1.refresh_from_db()
        self.assertEqual(order1.delivery, delivery)

        order2.refresh_from_db()
        self.assertEqual(order2.delivery, None)

        order3.refresh_from_db()
        self.assertEqual(order3.delivery, delivery)

        delivery.refresh_from_db()
        self.assertEqual(delivery.is_complete, False)
        self.assertEqual(test_earnings_factor, delivery.earnings_factor)

    def test_with_incomplete_delivery_2(self):
        """
        Тест с незавершенным заказом N2
        """
        courier = Courier.objects.get(id=2)
        delivery = Delivery.objects.create(
            courier=courier, earnings_factor=courier.earnings_factor)
        order1 = Order.objects.create(
            id=1, weight=Decimal('0.01'), region=22, delivery=delivery,
            complete_time=delivery.assign_time)
        order2 = Order.objects.create(
            id=2, weight=Decimal('10.01'), region=22, delivery=delivery)
        order3 = Order.objects.create(
            id=3, weight=Decimal('2.45'), region=22, delivery=delivery)
        order1.interval_set.create(min_time='00:00', max_time='23:59')
        order2.interval_set.create(min_time='00:00', max_time='23:59')
        order3.interval_set.create(min_time='00:00', max_time='23:59')

        expected_content = \
            '{' \
            '   "courier_id": 2, ' \
            '   "courier_type": "bike", ' \
            '   "regions": [1, 2, 3], ' \
            '   "working_hours": ["09:00-18:00"]' \
            '}'
        self.__test_request(2, '{"regions": [1, 2, 3]}', 200, expected_content)

        order1.refresh_from_db()
        self.assertEqual(order1.delivery, delivery)

        order2.refresh_from_db()
        self.assertEqual(order2.delivery, None)

        order3.refresh_from_db()
        self.assertEqual(order3.delivery, None)

        delivery.refresh_from_db()
        self.assertEqual(delivery.is_complete, True)

    def test_with_incomplete_delivery_3(self):
        """
        Тест с незавершенным заказом N3
        """
        courier = Courier.objects.get(id=2)
        delivery = Delivery.objects.create(
            courier=courier, earnings_factor=courier.earnings_factor)
        order1 = Order.objects.create(
            id=1, weight=Decimal('0.01'), region=22, delivery=delivery)
        order2 = Order.objects.create(
            id=2, weight=Decimal('10.01'), region=22, delivery=delivery)
        order3 = Order.objects.create(
            id=3, weight=Decimal('2.45'), region=22, delivery=delivery)
        order1.interval_set.create(min_time='10:00', max_time='10:01')
        order2.interval_set.create(min_time='11:32', max_time='23:06')
        order3.interval_set.create(min_time='17:30', max_time='18:15')

        expected_content = \
            '{' \
            '   "courier_id": 2, ' \
            '   "courier_type": "bike", ' \
            '   "regions": [22], ' \
            '   "working_hours": ["09:00-10:00"]' \
            '}'
        self.__test_request(
            2, '{"working_hours": ["09:00-10:00"]}', 200, expected_content
        )

        order1.refresh_from_db()
        self.assertEqual(order1.delivery, None)

        order2.refresh_from_db()
        self.assertEqual(order2.delivery, None)

        order3.refresh_from_db()
        self.assertEqual(order3.delivery, None)

        try:
            delivery.refresh_from_db()
            self.assert_(False, 'This delivery should not exists')
        except ObjectDoesNotExist:
            pass
