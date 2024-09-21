from typing import Generic, TypeVar

T = TypeVar('T')
E = TypeVar('E')

class Result(Generic[T, E]):
    def __init__(self, value: T = None, error: E = None):
        self.is_ok = False

        if value is not None:
            if error is not None:
                raise TypeError("Cannot initialize Result with both value and error")

            self.is_ok = True

        self.value: T = value
        self.error: E = error
