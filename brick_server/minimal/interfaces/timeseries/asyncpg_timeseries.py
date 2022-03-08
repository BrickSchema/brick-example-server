from brick_data.timeseries import AsyncpgTimeseries as BaseAsyncpgTimeseries

from brick_server.minimal.interfaces.timeseries.base_timeseries import BaseTimeseries


class AsyncpgTimeseries(BaseAsyncpgTimeseries, BaseTimeseries):
    def __init__(self, *args, **kwargs):
        super(AsyncpgTimeseries, self).__init__(*args, **kwargs)
