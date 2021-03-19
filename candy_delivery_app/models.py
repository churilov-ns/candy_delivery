from django.db import models


# =====================================================================================================================


class Courier(models.Model):
    """
    Данные о курьере
    """

    # Идентификор
    id = models.IntegerField(primary_key=True)

    # Тип
    type = models.TextField(max_length=5)


# =====================================================================================================================


class Order(models.Model):
    """
    Данные о заказе
    """

    # Идентификор
    id = models.IntegerField(primary_key=True)

    # Вес
    weight = models.FloatField()

    # Район
    region = models.IntegerField()

    # Назначенный курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.SET_NULL, null=True, default=None
    )

    # Время назначения заказа
    assign_time = models.DateTimeField(default=None, null=True)

    # Время выполнения заказа
    complete_time = models.DateTimeField(default=None, null=True)


# =====================================================================================================================


class Region(models.Model):
    """
    Район
    """

    # Идентификатор района
    code = models.IntegerField()

    # Курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE, null=True, default=None
    )


# =====================================================================================================================


class Interval(models.Model):
    """
    Интервал времени
    (рабочие часы курьера / часы доставки товара)
    """

    # Курьер
    courier = models.ForeignKey(
        Courier, on_delete=models.CASCADE, null=True, default=None
    )

    # Заказ
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, null=True, default=None
    )

    # Начало интервала
    start = models.TimeField()

    # Конец интервала
    end = models.TimeField()

    def __str__(self):
        return self.start.strftime('%H:%M') + '-' + self.end.strftime('%H:%M')
