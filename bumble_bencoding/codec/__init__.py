from .decoder import decode as _decode
from .encoder import encode as _encode

from .flatten import deflate_bytes, inflate_bytes


def encode[T](data: T, optimize=True) -> bytes:
    """Encode Python object to bytes."""
    data = _encode(data)
    if not optimize:
        return data
    mapping, encoded_data = deflate_bytes(data)
    deflated = _encode((mapping, encoded_data))
    if (len(deflated) + 1) >= len(data):
        return data
    return b"?" + deflated


def decode[T](data: bytes) -> T:
    """Decode bytes to Python object."""
    if not data.startswith(b"?"):
        return _decode(data)[0]
    data = data[1:]
    (mapping, encoded_data), _ = _decode(data)
    data = inflate_bytes(encoded_data, mapping)
    result, _ = _decode(data)
    return result


__all__ = ['encode', 'decode']
