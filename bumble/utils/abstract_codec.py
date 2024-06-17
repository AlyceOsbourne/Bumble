from dataclasses import dataclass
from typing import Callable
import operator

def get_name(func):
    if hasattr(func, 'func'):
        return func.func.__name__
    else:
        return func.__name__
def create_methods(self, other):
    encode = lambda data: other.encode(self.encode(data))
    decode = lambda data: self.decode(other.decode(data))
    encode.__name__ = f"{get_name(self.encode)} -> {get_name(other.encode)}"
    decode.__name__ = f"{get_name(other.decode)} -> {get_name(self.decode)}"
    return encode, decode


@dataclass(frozen=True, eq=True)
class Codec:
    """This class represents the base Strategy in this example"""
    encode: Callable[[bytes], bytes]
    decode: Callable[[bytes], bytes]

    def __or__[T: 'Codec'](self, other: T) -> 'Codec':
        return Codec(*create_methods(self, other))
    def __str__(self) -> str:
        return f"Codec(encode={get_name(self.encode)}, decode={get_name(self.decode)})"