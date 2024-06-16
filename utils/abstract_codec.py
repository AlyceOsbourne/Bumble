from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, eq=True)
class Codec:
    """This class represents the base Strategy in this example"""
    encode: Callable[[bytes], bytes]
    decode: Callable[[bytes], bytes]

    def __or__[T: 'Codec'](self, other: T) -> 'Codec':
        return Codec(
            encode=lambda data: other.encode(self.encode(data)),
            decode=lambda data: self.decode(other.decode(data))
        )  # type: ignore
