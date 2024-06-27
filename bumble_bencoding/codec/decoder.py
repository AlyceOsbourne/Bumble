"""Decoder module for various Python data types."""
import array
import decimal
import enum
import importlib
from collections import namedtuple
from typing import Any
import inspect
from bumble_bencoding.codec.exceptions import BumbleDecodeException


def decode(data: bytes, index: int = 0) -> tuple[Any, int]:
    """Helper function for decoding bytes to Python object."""
    if not data:
        raise BumbleDecodeException("Data must not be empty")

    def starts_with(seq: bytes) -> bool:
        """Check if data starts with a given sequence."""
        return data[index:index + len(seq)] == seq

    if data[index:index + 1].isdigit():
        return decode_bytes(data, index)
    elif starts_with(b'y'):
        return decode_type(data, index)
    elif starts_with(b'nt'):
        return decode_named_tuple(data, index)
    elif starts_with(b'+') or starts_with(b'-'):
        return data[index:index + 1] == b'+', index + 1
    elif starts_with(b'i'):
        return decode_int(data, index)
    elif starts_with(b'f'):
        return decode_float(data, index)
    elif starts_with(b'c'):
        return decode_complex(data, index)
    elif starts_with(b'u'):
        return decode_unicode(data, index)
    elif any(starts_with(ch) for ch in [b'l', b'd', b's', b't', b'L', b'D', b'S', b'T']):
        return decode_collection(data, index, data[index:index + 1])
    elif starts_with(b'o'):
        return decode_object(data, index)
    elif starts_with(b'n'):
        return None, index + 1
    elif starts_with(b'a'):
        return decode_array(data, index)
    elif starts_with(b'e'):
        return decode_enum(data, index)
    else:
        raise BumbleDecodeException(f"Invalid encoded data at index {index}")


def decode_int(data: bytes, index: int) -> tuple[int, int]:
    """Decode integer from bytes."""
    end_index = data.index(b'e', index)
    number_str = data[index + 1:end_index].decode()
    return int(number_str), end_index + 1


def decode_float(data: bytes, index: int) -> tuple[float, int]:
    """Decode float from bytes."""
    end_index = data.index(b'e', index)
    float_str = data[index + 1:end_index].decode()
    if float_str == '+':
        number = float('inf')
    elif float_str == '-':
        number = float('-inf')
    elif float_str == '?':
        number = float('nan')
    else:
        number = float(decimal.Decimal(float_str))
    return number, end_index + 1


def decode_complex(data: bytes, index: int) -> tuple[complex, int]:
    """Decode complex number from bytes."""
    real, index = decode_float(data, index + 1)
    imag, index = decode_float(data, index)
    return complex(real, imag), index


def decode_bytes(data: bytes, index: int) -> tuple[bytes, int]:
    """Decode bytes from bytes."""
    colon_index = data.index(b':', index)
    length = int(data[index:colon_index].decode())
    start = colon_index + 1
    end = start + length
    return data[start:end], end


def decode_unicode(data: bytes, index: int) -> tuple[str, int]:
    """Decode Unicode string from bytes."""
    colon_index = data.index(b':', index)
    length = int(data[index + 1:colon_index].decode())  # Skip 'u' character
    start = colon_index + 1
    end = start + length
    decoded_str = data[start:end].decode()
    return decoded_str, end


def decode_collection(data: bytes, index: int, type_char: bytes) -> tuple[list | dict | set | tuple, int]:
    """Decode collection (list, dict, set, tuple) from bytes."""
    if type_char in b"LDST":
        return initialize_collection(type_char), index + 1
    index += 1  # Skip the type character
    result = initialize_collection(type_char)
    while data[index:index + 1] != b'e':
        if type_char == b'd':
            key, index = decode(data, index)
            value, index = decode(data, index)
            result[key] = value
        else:
            item, index = decode(data, index)
            if type_char == b's':
                result.add(item)
            else:
                result.append(item)
    return finalize_collection(result, type_char), index + 1


def decode_array(data: bytes, index: int) -> tuple[array.array, int]:
    """Decode array from bytes."""
    array_type = data[index + 1:index + 2].decode()
    array_data, index = decode(data, index + 2)
    return array.array(array_type, array_data), index


def decode_obj_name(data):
    """Decode object name from import path."""
    return data.rsplit('.', 1)


def decode_object(data: bytes, index: int) -> tuple[Any, int]:
    """Decode arbitrary object from bytes."""
    index += 1  # Skip the 'o' character
    import_path, index = decode_unicode(data, index)
    attributes, index = decode_collection(data, index, data[index:index + 1])
    module_name, class_name = decode_obj_name(import_path)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    obj = cls.__new__(cls)
    if hasattr(obj, '__dict__'):
        obj.__dict__.update(attributes)
    if hasattr(obj, '__slots__'):
        for slot, value in attributes.items():
            setattr(obj, slot, value)
    return obj, index


def decode_enum(data: bytes, index: int) -> tuple[enum.Enum, int]:
    """Decode enum from bytes."""
    index += 1  # Skip the 'e' character
    import_path, index = decode_unicode(data, index)
    name, index = decode_unicode(data, index)
    module_name, class_name = import_path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls[name], index


def decode_named_tuple(data: bytes, index: int) -> tuple[namedtuple, int]:
    """Decode named tuple."""
    index += 2  # Skip the 'nt' character
    name, index = decode_unicode(data, index)
    fields, index = decode(data, index)
    return namedtuple(name, fields.keys())(*fields.values()), index


def initialize_collection(type_char: bytes) -> list | dict | set | tuple:
    """Initialize collection based on type character."""
    match type_char:
        case b'l' | b'L' | b't':
            return []
        case b'd' | b'D':
            return {}
        case b's' | b'S':
            return set()
        case b'T':
            return ()
        case _:
            raise ValueError(f"Invalid collection type: {type_char}")


def decode_type(data, index):
    """Decode type."""
    index += 1  # Skip the 'y' character
    module, index = decode_unicode(data, index)
    name, index = decode_unicode(data, index)
    return getattr(importlib.import_module(module), name), index


def finalize_collection(collection: list | dict | set | tuple, type_char: bytes) -> list | dict | set | tuple:
    """Finalize collection based on type character."""
    if type_char == b't':
        return tuple(collection)
    return collection


__all__ = ['decode']
