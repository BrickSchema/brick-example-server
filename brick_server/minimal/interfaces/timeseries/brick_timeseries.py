from brick_data.timeseries import BrickTimeseries

from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries


class BrickTimeseries(BrickTimeseries, BaseTimeseries):
    def __init__(self, *args, **kwargs):
        super(BrickTimeseries, self).__init__(*args, **kwargs)
