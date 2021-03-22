from decimal import Decimal
from ._object_wrapper import ObjectWrapper
from .order_wrapper import OrderWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'CourierWrapper',
]


# =====================================================================================================================


class CourierWrapper(ObjectWrapper):
    """
    'Обертка' для данных о курьере
    """

    # Тип модели объекта
    MODEL_TYPE = models.Courier

    def __init__(self, object_, select_related=False):
        self.type = None
        self.regions = list()
        self.working_hours = list()
        super().__init__(object_, select_related)

    def select_related_objects(self):
        """
        Загрузка связанных объектов из БД
        """
        self.type = self.object_.couriertype_set.latest('change_time')
        self.regions = list(self.object_.region_set.all())
        self.working_hours = list(self.object_.interval_set.all().order_by('min_time'))

    def clean_related_objects(self):
        """
        Проверка корректности данных связанных объектов
        """
        if self.type is not None:
            self.type.full_clean(exclude=['courier'])
        for region in self.regions:
            region.full_clean(exclude=['courier'])
        for interval in self.working_hours:
            interval.full_clean(exclude=['courier'])

    def save_related_objects(self, force_update=False):
        """
        Запись связанных объектов в БД
        :param bool force_update: флаг принудительной перезаписи данных
        """
        if self.type is not None:
            self.type.save()
        if force_update or len(self.regions) > 0:
            self.object_.region_set.all().delete()
        for region in self.regions:
            region.save()
        if force_update or len(self.working_hours) > 0:
            self.object_.interval_set.all().delete()
        for interval in self.working_hours:
            interval.save()

    def test_order(self, order_wrapper):
        """
        Проверка возможности назначения заказа (район, часы)
        :param OrderWrapper order_wrapper: заказ
        :return bool: True, если назначение возможно, иначе False
        """
        # Район
        if order_wrapper.object_.region not in self.regions:
            return False

        # Часы работы / доставки
        match_working_hours = False
        for working_interval in self.working_hours:
            for delivery_interval in order_wrapper.delivery_hours:
                if delivery_interval.intersects_with(working_interval):
                    match_working_hours = True
                    break
        return match_working_hours

    def test_weight(self, weight):
        """
        Проверка возможности назначения заказа (вес)
        :param Decimal weight: текущий вес развоза
        :return bool: True, если назначение возможно, иначе False
        """
        if self.type is None:
            return False
        else:
            return weight <= self.type.max_weight

    def to_json_data(self):
        """
        Конвертация в структуру данных для выдачи
        :return dict: данные для выдачи
        """
        courier_type = None if self.type is None else self.type.type
        return {
            'courier_id': self.object_.id,
            'courier_type': courier_type,
            'regions': [r.number for r in self.regions],
            'working_hours': [str(i) for i in self.working_hours],
        }
