"""Base Class for the Codecs in the Bumble Library"""
from dataclasses import dataclass
from typing import Callable


def get_name(func):
    """Get the name of the function. Accounts for partials."""
    if hasattr(func, 'func'):
        return get_name(func.func)
    else:
        return func.__name__


def create_methods(self, other):
    """Create the encode and decode methods for the new Codec."""
    encode = lambda data: other.encode(self.encode(data))  # noqa: E731
    decode = lambda data: self.decode(other.decode(data))  # noqa: E731

    self_encode_name = get_name(self.encode)
    self_decode_name = get_name(self.decode)
    other_encode_name = get_name(other.encode)
    other_decode_name = get_name(other.decode)

    encode.__name__ = f"{self_encode_name} -> {other_encode_name}"
    decode.__name__ = f"{other_decode_name} -> {self_decode_name}"

    encode.__str__ = lambda: f"{self_encode_name} -> {other_encode_name}"
    decode.__str__ = lambda: f"{other_decode_name} -> {self_decode_name}"

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
