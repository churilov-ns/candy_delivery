import re
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator


# =====================================================================================================================


class ObjectValidationError(ValidationError):
    """
    ...
    """

    def __init__(self, object_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object_id = object_id


# =====================================================================================================================


class RelatedObjectsMixin(object):
    """
    ...
    """

    def __init__(self):
        self.related_objects = list()

    def clean(self):
        for object_ in self.related_objects:
            object_.full_clean()

    def save_related_objects(self, *args, **kwargs):
        for object_ in self.related_objects:
            object_.save(*args, **kwargs)
        self.related_objects = list()


# =====================================================================================================================


class Courier(models.Model, RelatedObjectsMixin):
    """
    Данные о курьере
    """

    # Идентификатор
    id = models.IntegerField(
        primary_key=True,
        validators=[MinValueValidator(0)],
    )

    # Тип курьера
    class AllowedTypes(models.TextChoices):
        FOOT = 'foot'
        BIKE = 'bike'
        CAR = 'car'
    type = models.CharField(
        max_length=4,
        choices=AllowedTypes.choices,
    )

    @classmethod
    def from_item(cls, item):
        try:
            courier_id = item.pop('courier_id')
        except KeyError as e:
            raise ValidationError(
                'No "courier_id" parameter provided') from e

        courier = Courier(id=courier_id)
        courier.update(item, True)
        try:
            courier.full_clean()
            return courier
        except ValidationError as e:
            raise ObjectValidationError(
                courier_id, e.__str__()) from e

    def update(self, item, strict_mode=False):
        affected_fields = set()
        try:
            value = self._extract_value(item, 'courier_type', strict_mode)
            if value is not None:
                self.type = value
                affected_fields.add('courier_type')

            value = self._extract_value(item, 'regions', strict_mode)
            if value is not None:
                self.related_objects += Region.from_number_list(value, self)
                affected_fields.add('regions')

            value = self._extract_value(item, 'working_hours', strict_mode)
            if value is not None:
                self.related_objects += Interval.from_string_list(value, courier_fk=self)
                affected_fields.add('working_hours')

        except ValidationError as e:
            raise ObjectValidationError(
                self.id, e.__str__()) from e

        if len(item) > 0:
            raise ObjectValidationError(
                self.id, 'Unsupported parameters provided')
        return affected_fields

    def to_item(self):
        return {
            'courier_id': self.id,
            'courier_type': self.type,
            'regions': [r.number for r in self.region_set.all()],
            'working_hours': [str(i) for i in self.interval_set.all()],
        }

    @staticmethod
    def _extract_value(item, key, strict_mode):
        try:
            return item.pop(key)
        except KeyError as e:
            if strict_mode:
                raise ValidationError(
                    'Missing required parameter "{0}"'.format(key)) from e


# =====================================================================================================================


class Order(models.Model, RelatedObjectsMixin):
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
    assign_datetime = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
    )

    # Время выполнения заказа
    complete_datetime = models.DateTimeField(
        null=True,
        blank=True,
        default=None,
    )

    @classmethod
    def from_item(cls, item):
        try:
            order_id = item.pop('order_id')
        except KeyError as e:
            raise ValidationError(
                'No "order_id" parameter provided') from e

        order = Order(id=order_id)
        try:
            order.weight = str(item.pop('weight'))
            order.region = item.pop('region')
            order.related_objects += Interval.from_string_list(
                item.pop('delivery_hours'), order_fk=order
            )
        except KeyError as e:
            raise ObjectValidationError(
                order.id, 'Missing required parameters') from e
        except ValidationError as e:
            raise ObjectValidationError(
                order.id, e.__str__()) from e

        if len(item) > 0:
            raise ObjectValidationError(
                order.id, 'Unsupported parameters provided')

        try:
            order.full_clean()
            return order
        except ValidationError as e:
            raise ObjectValidationError(
                order_id, e.__str__()) from e


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
        try:
            return [
                Region(number=number, courier=courier_fk)
                for number in number_list
            ]
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
        return self.min_time.strftime('%H:%M') + \
               '-' + self.max_time.strftime('%H:%M')

    @classmethod
    def from_string(cls, string, *, courier_fk=None, order_fk=None):
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
        try:
            return [
                Interval.from_string(string, courier_fk=courier_fk, order_fk=order_fk)
                for string in string_list
            ]
        except TypeError as e:
            raise ValidationError(
                '"string_list" must be an iterable') from e
