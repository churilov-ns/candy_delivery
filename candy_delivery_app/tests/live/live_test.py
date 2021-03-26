import json
import pytz
import time
import unittest
import http.client
from datetime import timedelta
import pyrfc3339


# =====================================================================================================================


class CandyDeliveryAppLiveTest(unittest.TestCase):
    """
    Натуральный тест
    """

    def setUp(self):
        """
        Инициализация
        """
        self.tz = pytz.timezone('US/Alaska')
        self.conn = http.client.HTTPConnection(
            '0.0.0.0', 8080
        )

    def tearDown(self):
        """
        Завершение
        """
        self.conn.close()
        
    def _get_response(self):
        """
        Получить ответ по готовности
        """
        n_try = 0
        while n_try < 600:
            try:
                return self.conn.getresponse()
            except http.client.ResponseNotReady:
                time.sleep(1)
                n_try += 1
        self.assert_(False, 'No response from server')

    def _request(self, method, url):
        """
        Отправить обычный запрос
        """
        self.conn.request(method, url)
        return self._get_response()

    def _json_request(self, method, url, data):
        """
        Отправить JSON-запрос
        """
        self.conn.request(
            method, url, json.dumps(data),
            {'Content-Type': 'application/json'})
        return self._get_response()

    def _format_datetime(self, dt):
        """
        Дата/время -> строка
        """
        return pyrfc3339.generate(
            dt.astimezone(self.tz), utc=False, microseconds=True
        )

    def test_live(self):
        """
        Запуск теста
        """

        # 1) Добавились курьеры
        couriers = {
            'data': [
                {
                    'courier_id': 1,
                    'courier_type': 'foot',
                    'regions': [1, 2, 3],
                    'working_hours': ['09:00-13:00', '14:00-18:00'],
                },
                {
                    'courier_id': 2,
                    'courier_type': 'bike',
                    'regions': [3, 22],
                    'working_hours': ['08:00-10:00', '11:35-12:50', '17:10-20:30'],
                },
                {
                    'courier_id': 3,
                    'courier_type': 'car',
                    'regions': [1, 3, 31, 44, 55],
                    'working_hours': [],
                },
            ]
        }
        response = self._json_request('POST', '/couriers', couriers)
        self.assertEqual(response.status, 201)
        self.assertEqual(response.reason, 'Created')
        self.assertEqual(
            json.loads(response.read()), {
                'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]
            }
        )

        # 2) Первый решил посмотреть статистику сразу, но ошибся ID
        # FIXME: завешивает сервер!!!
        """
        response = self._request('GET', '/couriers/11')
        self.assertEqual(response.status, 404)
        self.assertEqual(response.reason, 'Not Found')
        """

        # 3) Собрался
        response = self._request('GET', '/couriers/1')
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['09:00-13:00', '14:00-18:00'],
                'earnings': 0,
            }
        )

        # 4) В систему добавились заказы
        orders = {
            'data': [
                {
                    'order_id': 1,
                    'weight': 0.5,
                    'region': 1,
                    'delivery_hours': ['18:00-23:00'],
                },
                {
                    'order_id': 2,
                    'weight': 4.32,
                    'region': 2,
                    'delivery_hours': ['11:00-15:45', '21:00-21:05'],
                },
                {
                    'order_id': 3,
                    'weight': 2,
                    'region': 2,
                    'delivery_hours': ['06:15-09:01'],
                },
                {
                    'order_id': 4,
                    'weight': 15.41,
                    'region': 99,
                    'delivery_hours': ['00:00-23:59'],
                },
            ]
        }
        response = self._json_request('POST', '/orders', orders)
        self.assertEqual(response.status, 201)
        self.assertEqual(response.reason, 'Created')
        self.assertEqual(
            json.loads(response.read()), {
                'orders': [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]
            }
        )

        # 5) Третий курьер собрался поработать
        response = self._json_request(
            'POST', '/orders/assign', {'courier_id': 3})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'orders': []
            }
        )

        # 6) Понял, что не завел часы работы
        response = self._json_request(
            'PATCH', '/couriers/3', {'working_hours': ['09:30-18:15']})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 3,
                'courier_type': 'car',
                'regions': [1, 3, 31, 44, 55],
                'working_hours': ['09:30-18:15'],
            }
        )

        # 7) Но было уже поздно...
        response = self._json_request(
            'POST', '/orders/assign', {'courier_id': 1})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        c1_d1 = json.loads(response.read())
        c1_d1_assign_time = pyrfc3339.parse(c1_d1['assign_time'])
        self.assertEqual(
            c1_d1['orders'], [{'id': 3}, {'id': 2}]
        )

        # 8) Третий берет заказ
        response = self._json_request(
            'POST', '/orders/assign', {'courier_id': 3})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        c3_d1 = json.loads(response.read())
        c3_d1_assign_time = pyrfc3339.parse(c3_d1['assign_time'])
        self.assertEqual(
            c3_d1['orders'], [{'id': 1}]
        )

        # 9) Первый завершает один заказ
        # C1 R2 1800
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 1, 'order_id': 3,
            'complete_time': self._format_datetime(
                c1_d1_assign_time + timedelta(seconds=1800.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 3,
            }
        )

        # 10) Третий завершает свой заказ - он же на тачке
        # C3+ R1 2150
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 3, 'order_id': 1,
            'complete_time': self._format_datetime(
                c3_d1_assign_time + timedelta(seconds=2150.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 1,
            }
        )

        # 11) Подъезжают еще заказы
        orders = {
            'data': [
                {
                    'order_id': 5,
                    'weight': 5,
                    'region': 22,
                    'delivery_hours': ['00:00-23:59'],
                },
                {
                    'order_id': 6,
                    'weight': 6,
                    'region': 22,
                    'delivery_hours': ['00:00-23:59'],
                },
                {
                    'order_id': 7,
                    'weight': 3.92,
                    'region': 22,
                    'delivery_hours': ['00:00-23:59'],
                },
                {
                    'order_id': 8,
                    'weight': 0.5,
                    'region': 3,
                    'delivery_hours': ['10:00-11:00'],
                },
                {
                    'order_id': 9,
                    'weight': 7.37,
                    'region': 3,
                    'delivery_hours': ['00:00-23:59'],
                },
                {
                    'order_id': 10,
                    'weight': 0.01,
                    'region': 2,
                    'delivery_hours': ['00:00-23:59'],
                },
            ]
        }
        response = self._json_request('POST', '/orders', orders)
        self.assertEqual(response.status, 201)
        self.assertEqual(response.reason, 'Created')
        self.assertEqual(
            json.loads(response.read()), {
                'orders': [
                    {'id': 5},
                    {'id': 6},
                    {'id': 7},
                    {'id': 8},
                    {'id': 9},
                    {'id': 10}
                ]
            }
        )

        # 12) Первый курьер завершает развоз
        # C1+ R2 1800 900
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 1, 'order_id': 2,
            'complete_time': self._format_datetime(
                c1_d1_assign_time + timedelta(seconds=2700.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 2,
            }
        )

        # 13) Второй курьер наконец-то берет заказы
        response = self._json_request(
            'POST', '/orders/assign', {'courier_id': 2})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        c2_d1 = json.loads(response.read())
        c2_d1_assign_time = pyrfc3339.parse(c2_d1['assign_time'])
        self.assertEqual(
            c2_d1['orders'], [{'id': 7}, {'id': 5}, {'id': 6}]
        )

        # 14) Первый курьер снова рвется в бой
        response = self._json_request(
            'POST', '/orders/assign', {'courier_id': 1})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        c1_d2 = json.loads(response.read())
        c1_d2_assign_time = pyrfc3339.parse(c1_d2['assign_time'])
        self.assertEqual(
            c1_d2['orders'], [{'id': 10}, {'id': 8}, {'id': 9}]
        )

        # 15) Второй курьер завершает заказ
        # C2 R22 300
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 2, 'order_id': 7,
            'complete_time': self._format_datetime(
                c2_d1_assign_time + timedelta(seconds=300.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 7,
            }
        )

        # 16) Первый курьер завершает заказ
        # C1+ R2 1800 900 R3 600
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 1, 'order_id': 8,
            'complete_time': self._format_datetime(
                c1_d2_assign_time + timedelta(seconds=600.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 8,
            }
        )

        # 17) У второго ломается велик и он теряет закза №6
        response = self._json_request(
            'PATCH', '/couriers/2', {'courier_type': 'foot'})
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 2,
                'courier_type': 'foot',
                'regions': [3, 22],
                'working_hours': ['08:00-10:00', '11:35-12:50', '17:10-20:30'],
            }
        )

        # 16) Первый курьер опять завершает заказ
        # C1+ R2 1800 900 R3 600 1320
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 1, 'order_id': 9,
            'complete_time': self._format_datetime(
                c1_d2_assign_time + timedelta(seconds=1920.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 9,
            }
        )

        # 17) Второй героически добивает развоз
        # C2+ R22 300 2200
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 2, 'order_id': 5,
            'complete_time': self._format_datetime(
                c2_d1_assign_time + timedelta(seconds=2500.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 5,
            }
        )

        # 18) Наш герой
        # C1++ R2 1800 900 800 R3 600 1320
        response = self._json_request('POST', '/orders/complete', {
            'courier_id': 1, 'order_id': 10,
            'complete_time': self._format_datetime(
                c1_d2_assign_time + timedelta(seconds=2720.)
            )
        })
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'order_id': 10,
            }
        )

        # 19) Время статистики: курьер 1
        response = self._request('GET', '/couriers/1')
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [1, 2, 3],
                'working_hours': ['09:00-13:00', '14:00-18:00'],
                'rating': 5. * (3600. - 960.) / 3600.,
                'earnings': 2000,
            }
        )

        # 20) Время статистики: курьер 2
        response = self._request('GET', '/couriers/2')
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 2,
                'courier_type': 'foot',
                'regions': [3, 22],
                'working_hours': ['08:00-10:00', '11:35-12:50', '17:10-20:30'],
                'rating': 5. * (3600. - 2500. / 2.) / 3600.,
                'earnings': 2500,
            }
        )

        # 21) Время статистики: курьер 3
        response = self._request('GET', '/couriers/3')
        self.assertEqual(response.status, 200)
        self.assertEqual(response.reason, 'OK')
        self.assertEqual(
            json.loads(response.read()), {
                'courier_id': 3,
                'courier_type': 'car',
                'regions': [1, 3, 31, 44, 55],
                'working_hours': ['09:30-18:15'],
                'rating': 5. * (3600. - 2150.) / 3600.,
                'earnings': 4500,
            }
        )


# =====================================================================================================================


# Запуск теста
if __name__ == "__main__":
    unittest.main()
