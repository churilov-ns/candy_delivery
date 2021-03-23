from ._object_wrapper import ObjectWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'OrderWrapper',
]


# =====================================================================================================================


class OrderWrapper(ObjectWrapper):
    """
    'Обертка' для данных о заказе
    """

    # Тип модели объекта
    MODEL_TYPE = models.Order

    def __init__(self, object_, select_related=False):
        """
        Инициализация
        :param int | models.Order object_: объект или id
        :param bool select_related: флаг загрузки связанных объектов
        """
        self.delivery_hours = list()
        super().__init__(object_, select_related)

    def select_related_objects(self):
        """
        Загрузка связанных объектов из БД
        """
        self.delivery_hours = list(self.object_.interval_set.all().order_by('min_time'))

    def clean_related_objects(self):
        """
        Проверка корректности данных связанных объектов
        """
        for interval in self.delivery_hours:
            interval.full_clean(exclude=['order'])

    def save_related_objects(self, force_update=False):
        """
        Запись связанных объектов в БД
        :param bool force_update: флаг принудительной перезаписи данных
        """
        if force_update or len(self.delivery_hours) > 0:
            self.object_.interval_set.all().delete()
        for interval in self.delivery_hours:
            interval.save()
