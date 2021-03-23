from decimal import Decimal
from django.test import TestCase
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportOrdersTest',
]


# =====================================================================================================================


class ImportOrdersTest(TestCase):
    """
    Тесты на регистрацию заказов в системе
    """

    # Отключить ограничение на вывод
    maxDiff = None

    def test_valid_request(self):
        """
        Корректный запрос
        """

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
        """
        Некорректный запрос
        """

        data = \
            '{' \
            '   "data": [' \
            '       {' \
            '           "order_id": 1,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 2,' \
            '           "weight": 0.23,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 3,' \
            '           "weight": 0.23,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 4,' \
            '           "weight": 0.23,' \
            '           "region": 12' \
            '       },' \
            '       {' \
            '           "order_id": 5,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "unknown_property": 100500,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            \
            \
            '       {' \
            '           "order_id": "6",' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": -6,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 6.5,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            \
            \
            '       {' \
            '           "order_id": 7,' \
            '           "weight": 0.231,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 8,' \
            '           "weight": 0.00,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 9,' \
            '           "weight": 50.01,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 10,' \
            '           "weight": "abc",' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            \
            \
            '       {' \
            '           "order_id": 11,' \
            '           "weight": 0.23,' \
            '           "region": -1,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 12,' \
            '           "weight": 0.23,' \
            '           "region": 1.5,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            '       {' \
            '           "order_id": 13,' \
            '           "weight": 0.23,' \
            '           "region": "my_best_region",' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       },' \
            \
            \
            '       {' \
            '           "order_id": 14,' \
            '           "weight": 0.23,' \
            '           "region": 1,' \
            '           "delivery_hours": "09:00-18:00"' \
            '       },' \
            '       {' \
            '           "order_id": 15,' \
            '           "weight": 0.23,' \
            '           "region": 1,' \
            '           "delivery_hours": {"a": 100, "b": 500}' \
            '       },' \
            '       {' \
            '           "order_id": 16,' \
            '           "weight": 0.23,' \
            '           "region": 1,' \
            '           "delivery_hours": ["09:15-18:00:35"]' \
            '       },' \
            '       {' \
            '           "order_id": 17,' \
            '           "weight": 0.23,' \
            '           "region": 1,' \
            '           "delivery_hours": []' \
            '       },' \
            '       {' \
            '           "order_id": 18,' \
            '           "weight": 0.23,' \
            '           "region": "my_best_region",' \
            '           "delivery_hours": ["18:00-09:00"]' \
            '       },' \
            \
            \
            '       {' \
            '           "order_id": 100,' \
            '           "weight": 0.23,' \
            '           "region": 12,' \
            '           "delivery_hours": ["09:00-18:00"]' \
            '       } ' \
            '   ]' \
            '}'
        response = self.client.post('/orders', data, 'application/json')
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(
            response.content,
            '{'
            '   "validation_error": {'
            '       "orders": ['
            '           {"id": 1}, '
            '           {"id": 2}, '
            '           {"id": 3}, '
            '           {"id": 4}, '
            '           {"id": 5}, '
            '           {"id": "6"}, '
            '           {"id": -6}, '
            '           {"id": 6.5}, '
            '           {"id": 7}, '
            '           {"id": 8}, '
            '           {"id": 9}, '
            '           {"id": 10}, '
            '           {"id": 11}, '
            '           {"id": 12}, '
            '           {"id": 13}, '
            '           {"id": 14}, '
            '           {"id": 15}, '
            '           {"id": 16}, '
            '           {"id": 17}, '
            '           {"id": 18} '
            '       ]'
            '   }'
            '}',
        )
