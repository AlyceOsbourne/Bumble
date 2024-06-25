"""The main bumble encoding and decoding functions."""
import array
import decimal
import enum
import importlib
import math
import types
from collections import namedtuple
from typing import Any


def _encode[T](data: T) -> bytes:
    """Helper function for encoding Python object."""
    match data:
        case enum.Enum():
            return _encode_enum(data)
        case array.array():
            return _encode_array(data)
        case bool():
            return b"+" if data else b"-"
        case complex():
            return _encode_complex(data)
        case int():
            return _encode_int(data)
        case float():
            return _encode_float(data)
        case bytes():
            return _encode_bytes(data)
        case str():
            return _encode_unicode(data)
        case list():
            return _encode_list(data)
        case dict():
            return _encode_dict(data)
        case set():
            return _encode_set(data)
        case tuple() if hasattr(data, '_fields'):
            return _encode_named_tuple(data)
        case tuple():
            return _encode_tuple(data)
        case None:
            return b"n"
        case _:
            return _encode_object(data)


def _encode_int(data: int) -> bytes:
    """Encode integer to bytes."""
    return f"i{data}e".encode()


def _encode_float(data: float) -> bytes:
    """Encode float to bytes."""
    if math.isinf(data):
        return b"f+e" if data > 0 else b"f-e"
    elif math.isnan(data):
        return b"f?e"
    else:
        return f"f{decimal.Decimal(str(data))}e".encode()


def _encode_complex(data: complex) -> bytes:
    """Encode complex number to bytes."""
    return b"c" + _encode_float(data.real) + _encode_float(data.imag) + b"e"


def _encode_bytes(data: bytes) -> bytes:
    """Encode bytes."""
    return f"{len(data)}:".encode() + data


def _encode_unicode(data: str) -> bytes:
    """Encode Unicode string."""
    encoded_data = data.encode()
    return f"u{len(encoded_data)}:".encode() + encoded_data


def _encode_list(data: list) -> bytes:
    """Encode list."""
    if not data:
        return b"L"
    return b"l" + b"".join(_encode(item) for item in data) + b"e"


def _encode_dict(data: dict) -> bytes:
    """Encode dictionary."""
    if not data:
        return b"D"
    return b"d" + b"".join(
        _encode(key) + _encode(value)
        for key, value in sorted(data.items())
    ) + b"e"


def _encode_set(data: set) -> bytes:
    """Encode set."""
    if not data:
        return b"S"
    return b"s" + b"".join(_encode(item) for item in sorted(data)) + b"e"


def _encode_tuple(data: tuple) -> bytes:
    """Encode tuple."""
    if not data:
        return b"T"
    return b"t" + b"".join(_encode(item) for item in data) + b"e"


def _encode_named_tuple(data: namedtuple) -> bytes:
    # we need to encode the name, and the fields like a dict
    return b"nt" + _encode_unicode(data.__class__.__name__) + _encode_dict(data._asdict()) + b"e"  # noqa


def _encode_array(data: array.array) -> bytes:
    """Encode array."""
    return f"a{data.typecode}".encode() + _encode(data.tolist())


def _encode_object(data: Any) -> bytes:
    """Encode arbitrary object."""
    import_path = f"{data.__class__.__module__}.{data.__class__.__qualname__}"
    attributes = {}
    if hasattr(data, '__dict__'):
        attributes.update(data.__dict__)
    if hasattr(data, '__slots__'):
        for slot in data.__slots__:
            attributes[slot] = getattr(data, slot)
    encoded_attributes = _encode_dict(attributes)
    return b"o" + _encode_unicode(import_path) + encoded_attributes


def _encode_enum(data: enum.Enum) -> bytes:
    """Encode enum."""
    import_path = f"{data.__class__.__module__}.{data.__class__.__qualname__}"
    return b"e" + _encode_unicode(import_path) + _encode_unicode(data.name)


def _decode[T](data: str, index: int) -> tuple[T, int]:
    """Helper function for decoding string to Python object."""

    def starts_with(seq: str) -> bool:
        """Check if data starts with a given sequence."""
        return data[index:index + len(seq)] == seq

    if data[index].isdigit():
        return _decode_bytes(data, index)
    elif starts_with('nt'):
        return _decode_named_tuple(data, index)
    elif starts_with('+') or starts_with('-'):
        return data[index] == '+', index + 1
    elif starts_with('i'):
        return _decode_int(data, index)
    elif starts_with('f'):
        return _decode_float(data, index)
    elif starts_with('c'):
        return _decode_complex(data, index)
    elif starts_with('u'):
        return _decode_unicode(data, index)
    elif any(starts_with(ch) for ch in ['l', 'd', 's', 't', 'L', 'D', 'S', 'T']):
        return _decode_collection(data, index, data[index])
    elif starts_with('o'):
        return _decode_object(data, index)
    elif starts_with('n'):
        return None, index + 1
    elif starts_with('a'):
        return _decode_array(data, index)
    elif starts_with('e'):
        return _decode_enum(data, index)
    else:
        raise BumbleDecodeException(f"Invalid encoded data at index {index}")


def _decode_int(data: str, index: int) -> tuple[int, int]:
    """Decode integer from string."""
    end_index = data.index('e', index)
    number_str = data[index + 1:end_index]
    return int(number_str), end_index + 1


def _decode_float(data: str, index: int) -> tuple[float, int]:
    """Decode float from string."""
    end_index = data.index('e', index)
    float_str = data[index + 1:end_index]
    if float_str == '+':
        number = float('inf')
    elif float_str == '-':
        number = float('-inf')
    elif float_str == '?':
        number = float('nan')
    else:
        number = float(decimal.Decimal(float_str))
    return number, end_index + 1


def _decode_complex(data: str, index: int) -> tuple[complex, int]:
    """Decode complex number from string."""
    real, index = _decode_float(data, index + 1)
    imag, index = _decode_float(data, index)
    return complex(real, imag), index


def _decode_bytes(data: str, index: int) -> tuple[bytes, int]:
    """Decode bytes from string."""
    colon_index = data.index(':', index)
    length = int(data[index:colon_index])
    start = colon_index + 1
    end = start + length
    return data[start:end].encode(), end


def _decode_unicode(data: str, index: int) -> tuple[str, int]:
    """Decode Unicode string from data."""
    colon_index = data.index(':', index)
    length = int(data[index + 1:colon_index])  # Skip 'u' character
    start = colon_index + 1
    end = start + length
    decoded_str = data[start:end].encode().decode()
    return decoded_str, end


def _decode_collection(data: str, index: int, type_char: str) -> tuple[list | dict | set | tuple, int]:
    """Decode collection (list, dict, set, tuple) from string."""
    if type_char in "LDST":
        return _initialize_collection(type_char), index + 1
    index += 1  # Skip the type character
    result = _initialize_collection(type_char)
    while data[index] != 'e':
        if type_char == 'd':
            key, index = _decode(data, index)
            value, index = _decode(data, index)
            result[key] = value
        else:
            item, index = _decode(data, index)
            if type_char == 's':
                result.add(item)
            else:
                result.append(item)
    return _finalize_collection(result, type_char), index + 1


def _decode_array(data: str, index: int) -> tuple[array.array, int]:
    """Decode array from string."""
    array_type = data[index + 1]
    array_data, index = _decode(data, index + 2)
    return array.array(array_type, array_data), index


def _decode_object(data: str, index: int) -> tuple[Any, int]:
    """Decode arbitrary object from string."""
    index += 1  # Skip the 'o' character
    import_path, index = _decode_unicode(data, index)
    attributes, index = _decode_collection(data, index, 'd')
    module_name, class_name = import_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    obj = cls.__new__(cls)
    if hasattr(obj, '__dict__'):
        obj.__dict__.update(attributes)
    if hasattr(obj, '__slots__'):
        for slot, value in attributes.items():
            setattr(obj, slot, value)
    return obj, index


def _decode_enum(data: str, index: int) -> tuple[enum.Enum, int]:
    """Decode enum from string."""
    index += 1  # Skip the 'e' character
    import_path, index = _decode_unicode(data, index)
    name, index = _decode_unicode(data, index)
    module_name, class_name = import_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls[name], index


def _decode_named_tuple(data: str, index: int) -> tuple[namedtuple, int]:
    index += 2  # Skip the 'nt' character
    name, index = _decode_unicode(data, index)
    fields, index = _decode(data, index)
    return namedtuple(name, fields.keys())(*fields.values()), index


def _initialize_collection(type_char: str) -> list | dict | set | tuple:
    """Initialize collection based on type character."""
    match type_char:
        case 'l' | 'L' | 't':
            return []
        case 'd' | 'D':
            return {}
        case 's' | 'S':
            return set()
        case 'T':
            return ()
        case _:
            raise ValueError(f"Invalid collection type: {type_char}")


def _finalize_collection(collection: list | dict | set | tuple, type_char: str) -> list | dict | set | tuple:
    """Finalize collection based on type character."""
    if type_char == 't':
        return tuple(collection)
    return collection


BumbleEncodeException = types.new_class('BumbleEncodeException', (Exception,))
BumbleDecodeException = types.new_class('BumbleDecodeException', (Exception,))
