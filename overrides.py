#!/usr/bin/python3
from builtins import bytes as bbytes
from typing import TypeVar, Type, Any

_T = TypeVar("_T")


class bytes(bbytes):
    """Local override of builtin bytes class to add "lazy_decode"

    bytes(iterable_of_ints) -> bytes
    bytes(string, encoding[, errors]) -> bytes
    bytes(bytes_or_buffer) -> immutable copy of bytes_or_buffer
    bytes(int) -> bytes object of size given by the parameter initialized with null bytes
    bytes() -> empty bytes object

    Construct an immutable array of bytes from:
      - an iterable yielding integers in range(256)
      - a text string encoded using the specified encoding
      - any object implementing the buffer API.
      - an integer
    """

    def __new__(
        cls: Type[_T],
        thing: Any = None,
        encoding: str = "UTF-8",
        errors: str = "strict",
    ) -> _T:
        if type(thing) == str:
            cls.value = super().__new__(cls, thing, encoding, errors)
        elif thing == None:
            cls.value = super().__new__(cls)
        elif thing != None:
            cls.value = super().__new__(cls, thing)
        else:
            raise AttributeError("wtf")
        return cls.value

    @classmethod
    def lazy_decode(self):
        return str(self.value)[2:-1]
