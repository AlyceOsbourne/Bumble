"""
.. include:: ../README.md
"""
import functools

from bumble.codec import _encode, _decode
from bumble.codec.exceptions import BumbleEncodeException, BumbleDecodeException


def encode[T](data: T) -> bytes:
    """Encode Python object to bytes."""
    return _encode(data)


def decode[T](data: bytes | str) -> T:
    """Decode bytes or string to Python object."""
    if isinstance(data, bytes):
        data = data.decode()
    if not isinstance(data, str):
        raise BumbleDecodeException("Data must be a string or bytes")
    result, _ = _decode(data, 0)
    return result

