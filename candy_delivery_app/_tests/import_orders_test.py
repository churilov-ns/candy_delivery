from decimal import Decimal
from django.test import TestCase
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportOrdersTest',
]


# =====================================================================================================================


class ImportOrdersTest(TestCase):

    def test_valid_request(self):
        data = \
            '{' \
            '   "data": [' \
            '       {' \
            '           "order_id": 1,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 2,' \
            '           "weight": 15,' \
            '           "region": 1,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 3,' \
            '           "weight": 0.01,' \
            '           "region": 22,' \
            '           "delivery_hours": ["09:00-12:00", "16:00-21:30"]' \
            '       }' \
            '   ]' \
            '}'
        response = self.client.post('/orders', data, 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(
            response.content,
            '{"orders": [{"id": 1}, {"id": 2}, {"id": 3}]}',
        )

        orders = models.Order.objects.all()
        self.assertEqual(len(orders), 3)
        for order in orders:
            if order.id == 1:
                expected_weight = Decimal('0.23')
                expected_region = 12
                expected_delivery_hours = ['09:00-18:00']
            elif order.id == 2:
                expected_weight = Decimal('15')
                expected_region = 1
                expected_delivery_hours = ['09:00-18:00']
            elif order.id == 3:
                expected_weight = Decimal('0.01')
                expected_region = 22
                expected_delivery_hours = ['09:00-12:00', '16:00-21:30']
            else:
                self.assert_(False, 'Wrong ID')
                break

            self.assertEqual(order.weight, expected_weight)
            self.assertEqual(order.region, expected_region)
            self.assertEqual(
                [str(i) for i in order.interval_set.all()],
                expected_delivery_hours,
            )

    def test_invalid_request(self):
        data = \
            '{' \
            '   "data": [' \
            '       {' \
            '           "order_id": 1,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 2,' \
            '           "weight": 15,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 3,' \
            '           "weight": 0.01,' \
            '           "region": 22,' \
            '           "delivery_hours": ["09:00-12:00", "16:00-21:30"],' \
            '           "unknown_property": 100500' \
            '       }' \
            '   ]' \
            '}'
        response = self.client.post('/orders', data, 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            '{"validation_error": {"orders": [{"id": 2}, {"id": 3}]}}',
        )
