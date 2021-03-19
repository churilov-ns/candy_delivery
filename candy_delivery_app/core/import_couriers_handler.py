from ._request_handler import RequestHandler
from ..models import Courier, Region, Interval


# =====================================================================================================================


__all__ = [
    'ImportCouriersHandler',
]


# =====================================================================================================================


class ImportCouriersHandler(RequestHandler):
    """
    Обработчик запроса на добавление курьеров
    """

    def _process(self, data):
        self.__couriers = list()
        self.__regions = list()
        self.__intervals = list()
        self.__invalid_ids = list()

        for item in data['data']:
            self.__parse_item(item)

        if len(self.__invalid_ids) > 0:
            self._status = 400
            self._content = {
                'validation_error': {
                    'couriers': self.__create_ids_list(
                        self.__invalid_ids),
                },
            }
        else:
            self.__save_data()
            self._status = 201
            self._content = {
                'couriers': self.__create_ids_list(
                    [c.id for c in self.__couriers]),
            }

    def __parse_item(self, item):
        courier_id = item.pop('courier_id')
        try:
            courier = Courier(id=courier_id, type=item.pop('courier_type'))
            self.__couriers.append(courier)

            for region in item.pop('regions'):
                self.__regions.append(Region(
                    code=region,
                    courier=courier,
                ))

            for interval in item.pop('working_hours'):
                parts = interval.split('-')
                self.__intervals.append(Interval(
                    start=parts[0],
                    end=parts[1],
                    courier=courier,
                ))

        except KeyError:
            self.__invalid_ids.append(courier_id)
            return

        if len(item) > 0:
            self.__invalid_ids.append(courier_id)

    def __save_data(self):
        for courier in self.__couriers:
            courier.save()
        for region in self.__regions:
            region.save()
        for interval in self.__intervals:
            interval.save()

    @staticmethod
    def __create_ids_list(ids):
        return [{'id': i} for i in ids]
