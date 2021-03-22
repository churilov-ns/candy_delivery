import re
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)


# =====================================================================================================================


class Courier(models.Model):
    """
    Данные о курьере
    """

    # Идентификатор
    id = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(0)],
    )


# =====================================================================================================================


class CourierType(models.Model):
    """
    История типов курьера
    """

    class AllowedTypes(models.TextChoices):
        """
        Возможные типы курьера
        """
        FOOT = 'foot'
        BIKE = 'bike'
        CAR = 'car'

    # Эпоха изменения
    change_time = models.DateTimeField(auto_now=True)

    # Тип курьера
    type = models.CharField(
        max_length=4, choices=AllowedTypes.choices,
    )

    # Курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE,
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


class Order(models.Model):
    """
    Данные о заказе
    """

    # Идентификор
    id = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(0)],
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
        validators=[MinValueValidator(0)],
    )

    # Назначенный курьер
    courier = models.ForeignKey(
        Courier,
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET_NULL,
    )

    # Время назначения заказа
    assign_time = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
    )

    # Время выполнения заказа
    complete_time = models.DateTimeField(
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
        validators=[MinValueValidator(0)],
    )

    # Курьер
    courier = models.ForeignKey(
        Courier,
        on_delete=models.CASCADE,
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
            return [
                Region(number=number, courier=courier_fk)
                for number in number_list
            ]
        except TypeError as e:
            raise ValidationError(
                '"number_list" must be an iterable'
            ) from e


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
            '([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2})').search(string)
        if match is None:
            raise ValidationError('Unsupported string format')
        i = Interval(
            min_time=match.groups()[0],
            max_time=match.groups()[1]
        )
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
