class BaseTimeseries:
    # def __init__(self, *args, **kwargs):
    #     pass

    async def add_data(self, domain_name, data):
        """Adds timeseries data

        This function adds data into the designated timeseries database.

        Args:
            data: A list of lists for timeseries data. An internal list represents a tuple of timestamped value for an entity. Refer to the data model `TimeseriesData` for the complete model.

        Returns:
            None. It raises an exception if it fails.

        Raises:
            TODO
        """
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )

    async def query(self, domain, entity_ids, start_time, end_time, limit=0, offset=0):
        """Executes a basic query over the timeseries DB.

        Processes a basic range-based query over the timeseries DB.

        Args:
            domain:
            start_time: UNIX timestamp in seconds as a floating point.
            end_time: UNIX timestamp in seconds as a floating point.
            entity_ids: A list of string entity identifiers.
            limit:
            offset:

        Returns:

        """
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )

    async def raw_query(self, qstr):
        """Executes SQL query over the timeseries DB.

        Executes SQL query over timeseries data.

        Args:
            qstr: A SQL query string. TODO: SQL template so that an implementation can be adapted for a different schema.

        Returns:
            TODO
        """
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )

    async def add_history_data(
        self, domain_name, entity_id, user_id, app_name, domain_user_app, time, value
    ):
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )
