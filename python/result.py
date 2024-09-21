from typing import TypeVar

T = TypeVar('T')
E = EypeVar('E')

class Result:
    def __init__(self, value: T = None, error: E = None):
        self.value = value
        self.error = error
