from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from . import models


class MyTest(SimpleTestCase):

    @staticmethod
    def test():
        i1 = models.Interval(
            min_time='12:32',
            max_time="18:00"
        )
        print(type(i1.min_time), ' ', i1.min_time)
        print(type(i1.max_time), ' ', i1.max_time)
        i1.clean_fields()

        try:
            c = models.Courier()
            c.id = 'abc'
            c.type = 152
            c.clean_fields()
        except ValidationError as e:
            print(e)

        try:
            c = models.Courier()
            c.id = -1
            c.type = 'bike'
            c.clean_fields()
        except ValidationError as e:
            print(e)
