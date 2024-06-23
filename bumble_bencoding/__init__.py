"""
.. include:: ../README.md
"""

from bumble_bencoding.codec import _encode, _decode  # noqa
from bumble_bencoding.codec.exceptions import BumbleDecodeException
from bumble_bencoding.utils.pipeline import Pipeline

__version__ = "0.0.1"

CONTROL_CHAR = "🐝".encode()  # used for verifying this is a bumble encoded object.


def encode[T](data: T) -> bytes:
    """Encode Python object to bytes."""
    return CONTROL_CHAR + _encode(data)


def decode[T](data: bytes | str) -> T:
    """Decode bytes to Python object."""
    if not data:
        raise BumbleDecodeException("Data must not be empty")
    if not data.startswith(CONTROL_CHAR):
        raise BumbleDecodeException("Invalid Data")
    data = data[len(CONTROL_CHAR):]
    if isinstance(data, bytes):
        data = data.decode()
    if not isinstance(data, str):
        raise BumbleDecodeException("Data must be a string or bytes")
    result, _ = _decode(data, 0)
    return result


__all__ = ['encode', 'decode', 'Pipeline', 'utils', 'codec']
