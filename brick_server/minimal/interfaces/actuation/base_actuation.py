from abc import ABC, abstractmethod

from multidict import MultiDict


class BaseActuation(ABC):
    # def __init__(self, *args, **kwargs):
    #     pass

    @abstractmethod
    async def actuate(self, entity_id: str, value, external_references: MultiDict):
        """Actuates an entity with a given value.

        This function sets the current value of the entity with `entity_id` as `value` in "the actual system" such as BACnet devices. The value may have a physical impact in the real world.

        Args:
            entity_id: The identifier of an entity.
            value: A numeric value that the request wants to actuate of the entity.
            external_references: External references from brick graph

        Returns:
            None. If the actuation is successful, the function completes. Otherwise, it raises an exception.

        Raises:
            TODO
        """
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )

    @abstractmethod
    async def read(self, entity_id: str, external_references: MultiDict):
        """Read the current value of an entity

        Args:
            entity_id: The identifier of an entity.
            external_references: External references from brick graph

        Returns:
            None. If the actuation is successful, the function completes. Otherwise, it raises an exception.

        Raises:
            TODO
        """
        raise NotImplementedError(
            "This should be overriden by an actual implementation."
        )
