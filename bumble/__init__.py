"""Everything contained in this module pertains to the codec itself."""
import functools

from bumble.codec import _encode, _decode
from bumble.constants import MODULE_MAPPING, REVERSE_MODULE_MAPPING
from bumble.exceptions import BumbleEncodeException, BumbleDecodeException
from bumble.helpers import _initialize_collection, _finalize_collection


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

