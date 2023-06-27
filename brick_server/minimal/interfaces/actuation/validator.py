from abc import ABC, abstractmethod


class ActuationValidator(ABC):
    def __init__(self):
        self.priority = 0

    @abstractmethod
    def __call__(self, value, *args, **kwargs) -> bool:
        raise NotImplementedError()


class ActuationValidatorIsOdd(ActuationValidator):
    def __init__(self):
        super().__init__()
        self.priority = 1

    def __call__(self, value, *args, **kwargs) -> bool:
        if not isinstance(value, int):
            raise ValueError()
        return value % 2 == 1


class ActuationValidatorIsEven(ActuationValidator):
    def __init__(self):
        super().__init__()
        self.priority = 1

    def __call__(self, value, *args, **kwargs) -> bool:
        if not isinstance(value, int):
            raise ValueError()
        return value % 2 == 0


class ActuationValidatorIsPrime(ActuationValidator):
    def __init__(self):
        super().__init__()
        self.priority = 2
        self.primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

    def __call__(self, value, *args, **kwargs) -> bool:
        if not isinstance(value, int) or value <= 0 or value > 50:
            raise ValueError()
        return value in self.primes


actuation_validators = [
    ActuationValidatorIsOdd(),
    # ActuationValidatorIsEven(),
    ActuationValidatorIsPrime(),
]
actuation_validators.sort(key=lambda x: -x.priority)


def validate_actuation(value) -> bool:
    for validator in actuation_validators:
        try:
            return bool(validator(value))
        except Exception:
            pass
    return False


if __name__ == "__main__":
    print(validate_actuation(1))
    print(validate_actuation(2))
    print(validate_actuation(4))
    print(validate_actuation(51))
    print(validate_actuation(52))
