from django.test import TestCase
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportCouriersTest',
]


# =====================================================================================================================


class ImportCouriersTest(TestCase):

    def test_valid_request(self):
        data = \
            '{' \
            '   "data": [' \
            '       {' \
            '           "courier_id": 1, ' \
            '           "courier_type": "foot", ' \
            '           "regions": [1, 12, 22], ' \
            '           "working_hours": ["11:35-14:05", "09:00-11:00"]' \
            '       },' \
            '       {' \
            '           "courier_id": 2,' \
            '           "courier_type": "bike",' \
            '           "regions": [22],' \
            '           "working_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "courier_id": 3,' \
            '           "courier_type": "car",' \
            '           "regions": [12, 22, 23, 33],' \
            '           "working_hours": []' \
            '       }' \
            '   ]' \
            '}'
        response = self.client.post('/couriers', data, 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(
            response.content,
            '{"couriers": [{"id": 1}, {"id": 2}, {"id": 3}]}',
        )

        couriers = models.Courier.objects.all()
        self.assertEqual(len(couriers), 3)
        for courier in couriers:
            if courier.id == 1:
                expected_type = 'foot'
                expected_regions = [1, 12, 22]
                expected_working_hours = ['11:35-14:05', '09:00-11:00']
            elif courier.id == 2:
                expected_type = 'bike'
                expected_regions = [22]
                expected_working_hours = ['09:00-18:00']
            elif courier.id == 3:
                expected_type = 'car'
                expected_regions = [12, 22, 23, 33]
                expected_working_hours = []
            else:
                self.assert_(False, 'Wrong ID')
                break

            self.assertEqual(
                courier.couriertype_set.latest('change_time').type, expected_type
            )
            self.assertEqual(
                [r.number for r in courier.region_set.all()],
                expected_regions
            )
            self.assertEqual(
                [str(i) for i in courier.interval_set.all()],
                expected_working_hours,
            )

    def test_invalid_request(self):
        data = \
            '{' \
            '   "data": [' \
            '       {' \
            '           "courier_id": 1, ' \
            '           "courier_type": "foot", ' \
            '           "regions": [1, 12, 22], ' \
            '           "working_hours": ["11:35-14:05", "09:00-11:00"]' \
            '       },' \
            '       {' \
            '           "courier_id": 2,' \
            '           "regions": [22],' \
            '           "working_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "courier_id": 3,' \
            '           "courier_type": "car",' \
            '           "regions": [12, 22, 23, 33],' \
            '           "working_hours": [],' \
            '           "unknown_field": 100500' \
            '       },' \
            '       {' \
            '           "courier_id": 4,' \
            '           "courier_type": "car",' \
            '           "regions": [],' \
            '           "working_hours": [152, "eeee"]' \
            '       },' \
            '       {' \
            '           "courier_id": "abc",' \
            '           "courier_type": "bus",' \
            '           "regions": ["one", "two", "three"],' \
            '           "working_hours": ["09-10:15", 152, "eeee"]' \
            '       },' \
            '       {' \
            '           "courier_id": 5,' \
            '           "courier_type": "bus",' \
            '           "regions": [],' \
            '           "working_hours": []' \
            '       }' \
            '   ]' \
            '}'
        response = self.client.post('/couriers', data, 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            '{"validation_error": {"couriers": [{"id": 2}, {"id": 3}, {"id": 4}, {"id": "abc"}, {"id": 5}]}}',
        )
