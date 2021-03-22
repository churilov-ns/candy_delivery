from django.core.exceptions import ValidationError
from ._import_handler import ImportHandler, ObjectValidationError
from ..wrappers import CourierWrapper
from .. import models


# =====================================================================================================================


__all__ = [
    'ImportCouriersHandler',
]


# =====================================================================================================================


class ImportCouriersHandler(ImportHandler):
    """
    Обработчик запроса на добавление курьеров
    """

    # Имя параметра, содержащего
    # список id в ответе
    _OUTPUT_KEY = 'couriers'

    @staticmethod
    def _init_object(item):
        """
        Формирование объекта по данным элемента запроса
        :param item: элемент запроса
        :return: объект
        """
        cw = CourierWrapper(item.pop('courier_id'))
        try:
            cw.object_.type = item.pop('courier_type')
            cw.regions = models.Region.from_number_list(
                item.pop('regions'), cw.object_
            )
            cw.working_hours = models.Interval.from_string_list(
                item.pop('working_hours'), courier_fk=cw.object_
            )
            cw.clean()
        except (KeyError, ValidationError) as e:
            raise ObjectValidationError(
                cw.object_.id, str(e)) from e

        if len(item) > 0:
            raise ObjectValidationError(
                cw.object_.id, 'Unsupported properties provided'
            )

        return cw

    @staticmethod
    def _save_object(object_):
        """
        Запись объекта в БД
        :param object_: объект для записи
        :return int: идентификатор сохраненного объекта
        """
        object_.save()
        return object_.object_.id
