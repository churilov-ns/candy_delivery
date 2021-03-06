import re
from datetime import time
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


# =====================================================================================================================


class Courier(models.Model):
    """
    Данные о курьере
    """

    class AllowedTypes(models.TextChoices):
        """
        Возможные типы курьера
        """
        FOOT = 'foot'
        BIKE = 'bike'
        CAR = 'car'

    # Идентификатор
    id = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(1)],
    )

    # Тип курьера
    type = models.CharField(
        max_length=4, choices=AllowedTypes.choices,
    )

    @property
    def max_weight(self):
        """
        Получение максимального веса
        :return Decimal: максимальный вес
        """
        if self.type == self.AllowedTypes.FOOT:
            return Decimal('10.00')
        elif self.type == self.AllowedTypes.BIKE:
            return Decimal('15.00')
        elif self.type == self.AllowedTypes.CAR:
            return Decimal('50.00')

    @property
    def earnings_factor(self):
        """
        Получение к-та для расчета заработка
        :return int: к-та для расчета заработка
        """
        if self.type == self.AllowedTypes.FOOT:
            return 2
        elif self.type == self.AllowedTypes.BIKE:
            return 5
        elif self.type == self.AllowedTypes.CAR:
            return 9


# =====================================================================================================================


class Delivery(models.Model):
    """
    Данные о развозе
    """

    # Назначенный курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE
    )

    # Коэффициент для расчета заработка
    earnings_factor = models.IntegerField()

    # Время назначения развоза
    assign_time = models.DateTimeField(
        default=timezone.now
    )

    # Признак завершения развоза
    is_complete = models.BooleanField(
        default=False
    )

    def update_complete(self):
        """
        Проверка и обновление
        признака завершения развоза
        """
        incomplete_orders = self.order_set.filter(
            complete_time=None)
        self.is_complete = len(incomplete_orders) == 0
        self.save()


# =====================================================================================================================


class Order(models.Model):
    """
    Данные о заказе
    """

    # Идентификор
    id = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(1)],
    )

    # Вес
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal('0.01')),
            MaxValueValidator(Decimal('50.00')),
        ],
    )

    # Район
    region = models.IntegerField(
        validators=[MinValueValidator(1)],
    )

    # Развоз
    delivery = models.ForeignKey(
        Delivery,
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )

    # Время выполнения заказа
    complete_time = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
    )

    # Время доставки (в секундах)
    delivery_duration = models.FloatField(
        null=True,
        blank=True,
        default=None,
    )


# =====================================================================================================================


class Region(models.Model):
    """
    Район
    """

    # Идентификатор района
    number = models.IntegerField(
        validators=[MinValueValidator(1)],
    )

    # Курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE,
    )

    @classmethod
    def from_number_list(cls, number_list, courier_fk):
        """
        Формирование списка объектов Region
        :param list(int) number_list: список номеров районов
        :param int | Courier courier_fk: внешний ключ на курьера
        :return list(Region): список объектов Region
        """
        try:
            regions = list()
            for number in number_list:
                if not isinstance(number, int):
                    raise ValidationError(
                        'Elements of "number_list" must be a type of int')
                regions.append(Region(number=number, courier=courier_fk))
            return regions

        except TypeError as e:
            raise ValidationError(
                '"number_list" must be an iterable') from e


# =====================================================================================================================


class Interval(models.Model):
    """
    Интервал времени
    (рабочие часы курьера / часы доставки товара)
    """

    # Начало интервала
    min_time = models.TimeField()

    # Конец интервала
    max_time = models.TimeField()

    # Курьер
    courier = models.ForeignKey(
        Courier,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )

    # Заказ
    order = models.ForeignKey(
        Order,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        """
        Получение строкового представления
        :return str: строковое представление
        """
        return '{0}-{1}'.format(
            self.min_time.strftime('%H:%M'),
            self.max_time.strftime('%H:%M')
        )

    def clean(self):
        """
        Валидация данных
        """
        if self.max_time <= self.min_time:
            raise ValidationError(
                '"min_time" must be less than "max_time"'
            )

    def intersects_with(self, other_interval):
        """
        Проверка пересечения интервалов
        :param Interval other_interval: интервал для проверки
        :return bool: результат проверки
        """
        if self.max_time <= other_interval.min_time:
            return False
        elif self.min_time >= other_interval.max_time:
            return False
        else:
            return True

    @classmethod
    def from_string(cls, string, *, courier_fk=None, order_fk=None):
        """
        Создание объекта Interval из строки формата '%H:%M-%H:%M'
        :param str string: строка
        :param int | Courier | None courier_fk: внешний ключ на курьера
        :param int | Order | None order_fk: внешний ключ на заказ
        :return Interval: интервал
        """
        match = re.compile(
            '^([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2})$').search(string)
        if match is None:
            raise ValidationError('Unsupported string format')

        try:
            i = Interval(
                min_time=time.fromisoformat(match.groups()[0]),
                max_time=time.fromisoformat(match.groups()[1])
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e

        if courier_fk is not None:
            i.courier = courier_fk
        elif order_fk is not None:
            i.order = order_fk

        return i

    @classmethod
    def from_string_list(cls, string_list, *, courier_fk=None, order_fk=None):
        """
        Создание списка объектов Interval из списка строк формата '%H:%M-%H:%M'
        :param list(str) string_list: список строк
        :param int | Courier | None courier_fk: внешний ключ на курьера
        :param int | Order | None order_fk: внешний ключ на заказ
        :return list(Interval): список объектов Interval
        """
        try:
            return [
                Interval.from_string(
                    string, courier_fk=courier_fk, order_fk=order_fk)
                for string in string_list
            ]
        except TypeError as e:
            raise ValidationError(
                '"string_list" must be an iterable'
            ) from e
