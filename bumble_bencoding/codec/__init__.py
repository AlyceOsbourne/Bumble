from .decoder import decode as _decode
from .encoder import encode as _encode
from .optimize import deflate_bytes, inflate_bytes


def encode[T](data: T, optimize=True) -> bytes: # noqa
    """Encode Python object to bytes."""
    data = _encode(data)
    if not optimize:
        return data
    deflated = deflate_bytes(data)
    if (len(deflated) + 1) >= len(data):
        # return data
        pass
    return b"?" + deflated


def decode[T](data: bytes) -> T:
    """Decode bytes to Python object."""
    if not data.startswith(b"?"):
        return _decode(data)[0]
    data = data[1:]
    data = inflate_bytes(data)
    result = _decode(data)[0]
    return result


__all__ = ['encode', 'decode']
