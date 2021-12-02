from werkzeug import exceptions


class BaseActuation(object):
    def __init__(self, *args, **kwargs):
        pass

    def actuate(self, entity_id, value):
        """Actuates an entity with a given value.

        This function sets the current value of the entity with `entity_id` as `value` in "the actual system" such as BACnet devices. The value may have a physical impact in the real world.

        Args:
            entity_id: The identifier of an entity.
            value: A numeric value that the request wants to actuate of the entity.

        Returns:
            None. If the actuation is successful, the function completes. Otherwise, it raises an exception.

        Raises:
            TODO
        """
        raise exceptions.NotImplemented(
            "This should be overriden by an actual implementation."
        )
