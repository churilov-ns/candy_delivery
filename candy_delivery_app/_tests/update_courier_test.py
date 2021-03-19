from django.test import TestCase
from ..models import Courier, Region, Interval


# =====================================================================================================================


__all__ = [
    'UpdateCourierTest',
]


# =====================================================================================================================


class UpdateCourierTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        Courier.objects.create(id=1, type='foot')
        Region.objects.create(courier_id=1, code=1)
        Region.objects.create(courier_id=1, code=12)
        Region.objects.create(courier_id=1, code=22)
        Interval.objects.create(courier_id=1, start='11:35', end='14:05')
        Interval.objects.create(courier_id=1, start='09:00', end='11:00')

        Courier.objects.create(id=2, type='bike')
        Region.objects.create(courier_id=2, code=22)
        Interval.objects.create(courier_id=2, start='09:00', end='18:00')

        Courier.objects.create(id=3, type='car')
        Region.objects.create(courier_id=3, code=12)
        Region.objects.create(courier_id=3, code=22)
        Region.objects.create(courier_id=3, code=23)
        Region.objects.create(courier_id=3, code=33)

    def test_valid_requests(self):
        data = \
            '{' \
            '   "courier_type": "car"' \
            '}'
        expected_content = \
            '{' \
            '   "courier_id": 1, ' \
            '   "courier_type": "car", ' \
            '   "regions": [1, 12, 22], ' \
            '   "working_hours": ["11:35-14:05", "09:00-11:00"]' \
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
        self.__test_request(100, '{}', 404, None)

        data = \
            '{' \
            '   "regions": [1, 5], ' \
            '   "working_hours": ["09:00-18:00", "19:05-23:55"],' \
            '   "unknown_field": 100500' \
            '}'
        self.__test_request(1, data, 400, None)

    def __test_request(self, courier_id, data, expected_status, expected_content):
        response = self.client.patch(
            '/couriers/{0}'.format(courier_id), data, 'application/json')
        self.assertEqual(response.status_code, expected_status)
        if expected_content is None:
            self.assertEqual(response.content, b'')
        else:
            self.assertJSONEqual(response.content, expected_content)
