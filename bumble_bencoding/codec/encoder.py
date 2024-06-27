"""Encoder module for various Python data types."""
import array
import decimal
import enum
import math
from collections import namedtuple
from typing import Any


def encode(data: Any) -> bytes:
    """Helper function for encoding Python object."""
    match data:
        case type():
            return encode_type(data)
        case enum.Enum():
            return encode_enum(data)
        case array.array():
            return encode_array(data)
        case bool():
            return b"+" if data else b"-"
        case complex():
            return encode_complex(data)
        case int():
            return encode_int(data)
        case float():
            return encode_float(data)
        case bytes():
            return encode_bytes(data)
        case str():
            return encode_unicode(data)
        case list():
            return encode_list(data)
        case dict():
            return encode_dict(data)
        case set():
            return encode_set(data)
        case tuple() if hasattr(data, '_fields'):
            return encode_named_tuple(data)
        case tuple():
            return encode_tuple(data)
        case None:
            return b"n"
        case _:
            return encode_object(data)


def encode_int(data: int) -> bytes:
    """Encode integer to bytes."""
    return f"i{data}e".encode()


def encode_float(data: float) -> bytes:
    """Encode float to bytes."""
    if math.isinf(data):
        return b"f+e" if data > 0 else b"f-e"
    elif math.isnan(data):
        return b"f?e"
    else:
        return f"f{decimal.Decimal(str(data))}e".encode()


def encode_complex(data: complex) -> bytes:
    """Encode complex number to bytes."""
    return b"c" + encode_float(data.real) + encode_float(data.imag) + b"e"


def encode_bytes(data: bytes) -> bytes:
    """Encode bytes."""
    return f"{len(data)}:".encode() + data


def encode_unicode(data: str) -> bytes:
    """Encode Unicode string."""
    encoded_data = data.encode()
    return f"u{len(encoded_data)}:".encode() + encoded_data


def encode_list(data: list) -> bytes:
    """Encode list."""
    if not data:
        return b"L"
    return b"l" + b"".join(encode(item) for item in data) + b"e"


def encode_dict(data: dict) -> bytes:
    """Encode dictionary."""
    if not data:
        return b"D"
    return b"d" + b"".join(
        encode(key) + encode(value)
        for key, value in sorted(data.items())
    ) + b"e"


def encode_set(data: set) -> bytes:
    """Encode set."""
    if not data:
        return b"S"
    return b"s" + b"".join(encode(item) for item in sorted(data)) + b"e"


def encode_tuple(data: tuple) -> bytes:
    """Encode tuple."""
    if not data:
        return b"T"
    return b"t" + b"".join(encode(item) for item in data) + b"e"


def encode_named_tuple(data: namedtuple) -> bytes:
    """Encode named tuple."""
    return b"nt" + encode_unicode(data.__class__.__name__) + encode_dict(data._asdict()) + b"e"  # noqa


def encode_array(data: array.array) -> bytes:
    """Encode array."""
    return f"a{data.typecode}".encode() + encode(data.tolist())


def encode_obj_name(data):
    """Encode object name."""
    return f"{data.__class__.__module__}.{data.__class__.__qualname__}"


def encode_object(data: Any) -> bytes:
    """Encode arbitrary object."""
    import_path = encode_obj_name(data)
    attributes = {}
    if hasattr(data, '__dict__'):
        attributes.update(data.__dict__)
    if hasattr(data, '__slots__'):
        for slot in data.__slots__:
            attributes[slot] = getattr(data, slot)
    encoded_attributes = encode_dict(attributes)
    return b"o" + encode_unicode(import_path) + encoded_attributes


def encode_enum(data: enum.Enum) -> bytes:
    """Encode enum."""
    import_path = f"{data.__class__.__module__}.{data.__class__.__qualname__}"
    return b"e" + encode_unicode(import_path) + encode_unicode(data.name)


def encode_type(data: type) -> bytes:
    """Encode type."""
    return b"y" + encode_unicode(data.__module__) + encode_unicode(data.__qualname__)



__all__ = ['encode']
