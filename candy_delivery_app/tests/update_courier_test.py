from django.test import TestCase
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

    @classmethod
    def setUpTestData(cls):
        """
        Инициализация тестовых данных
        """
        Courier.objects.create(id=1, type='foot')
        Region.objects.create(courier_id=1, number=1)
        Region.objects.create(courier_id=1, number=12)
        Region.objects.create(courier_id=1, number=22)
        Interval.objects.create(courier_id=1, min_time='09:00', max_time='11:00')
        Interval.objects.create(courier_id=1, min_time='11:35', max_time='14:05')

        Courier.objects.create(id=2, type='bike')
        Region.objects.create(courier_id=2, number=22)
        Interval.objects.create(courier_id=2, min_time='09:00', max_time='18:00')

        Courier.objects.create(id=3, type='car')
        Region.objects.create(courier_id=3, number=12)
        Region.objects.create(courier_id=3, number=22)
        Region.objects.create(courier_id=3, number=23)
        Region.objects.create(courier_id=3, number=33)

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

        self.__test_request(100, '{}', 404, None)

        data = \
            '{' \
            '   "regions": [1, 5], ' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"],' \
            '   "unknown_field": 100500' \
            '}'
        self.__test_request(1, data, 400, None)

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
