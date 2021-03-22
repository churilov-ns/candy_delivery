import abc
from django.db.models import Model


# =====================================================================================================================


__all__ = [
    'ObjectWrapper',
]


# =====================================================================================================================


class ObjectWrapper(abc.ABC):
    """
    'Обертка' для некоторого объекта
    """

    # Тип модели объекта
    MODEL_TYPE = Model

    def __init__(self, object_, select_related=False):
        """
        Инициализация
        :param object_: объект типа MODEL_TYPE или id
        :param bool select_related: флаг загрузки связанных объектов
        """
        if isinstance(object_, self.MODEL_TYPE):
            self.object_ = object_
        else:
            self.object_ = self.MODEL_TYPE(id=object_)

        if select_related:
            self.select_related_objects()

    @classmethod
    def select(cls, object_id, select_related=True):
        """
        Загрузка данных из БД
        :param int object_id: id объекта
        :param bool select_related: флаг загрузки связанных объектов
        :return ObjectWrapper: объект ObjectWrapper
        """
        wrapper = cls(cls.MODEL_TYPE.objects.get(id=object_id))
        if select_related:
            wrapper.select_related_objects()
        return wrapper

    @abc.abstractmethod
    def select_related_objects(self):
        """
        Загрузка связанных объектов из БД
        """
        pass

    def refresh(self):
        """
        Обновление данных
        """
        self.object_.refresh_from_db()
        self.select_related_objects()

    def clean(self):
        """
        Валидация данных
        """
        self.object_.full_clean()
        self.clean_related_objects()

    @abc.abstractmethod
    def clean_related_objects(self):
        """
        Проверка корректности данных связанных объектов
        """
        pass

    def save(self, force_update=False):
        """
        Запись данных в БД
        :param bool force_update: флаг принудительной перезаписи данных
        """
        self.object_.save()
        self.save_related_objects(force_update)

    @abc.abstractmethod
    def save_related_objects(self, force_update=False):
        """
        Запись связанных объектов в БД
        :param bool force_update: флаг принудительной перезаписи данных
        """
        pass
