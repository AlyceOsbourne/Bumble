import base64
import decimal
import importlib
import math
from typing import Any

MODULE_MAPPING: dict[str, str] = {
    "__main__": "?M",
    "builtins": "?b",
    "typing": "?t",
    "types": "?T",
    "math": "?m",
    "collections": "?c",
    "functools": "?f",
    "enum": "?e",
    "dataclasses": "?d",
    "decimal": "?D",
    "base64": "?B",
    "binascii": "?a",
    "importlib": "?i",
    "hashlib": "?h",
    "lzma": "?l",
    "zlib": "?z",
    "bz2": "?B",
    "gzip": "?g",
    "pickle": "?p",
    "json": "?j",
}

REVERSE_MODULE_MAPPING: dict[str, str] = {v: k for k, v in MODULE_MAPPING.items()}


def encode[T](data: T) -> bytes:
    return _encode(data)


def decode[T](data: bytes) -> T:
    if isinstance(data, bytes):
        data = data.decode()
    if not isinstance(data, str):
        raise TypeError("Data must be a string or bytes")
    result, _ = _decode(data, 0)
    return result


def _encode[T](data: T) -> bytes:
    match data:
        case bool():
            return b"b1" if data else b"b0"
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
        case tuple():
            return _encode_tuple(data)
        case None:
            return b"n"
        case _:
            return _encode_object(data)


def _decode[T](data: str, index: int) -> tuple[T, int]:
    match char := data[index]:
        case 'b':
            return _decode_bool(data, index)
        case 'i':
            return _decode_int(data, index, int)
        case 'f':
            return _decode_float(data, index)
        case 'u':
            return _decode_unicode(data, index)
        case _ if char.isdigit():
            return _decode_bytes(data, index)
        case 'l' | 'd' | 's' | 't' | 'L' | 'D' | 'S' | 'T':
            return _decode_collection(data, index, char)
        case 'o':
            return _decode_object(data, index)
        case 'n':
            return None, index + 1
        case _:
            raise ValueError("Invalid encoded data")


def _encode_int(data: int) -> bytes:
    length = data.bit_length()
    if length < 8:
        return f"i{data}e".encode()
    return f"i{base64.b85encode(data.to_bytes((length + 7) // 8, signed=True)).decode()}e".encode()


def _decode_int(data: str, index: int, cast_func: type) -> tuple[int, int]:
    end_index = data.index('e', index)
    number_str = data[index + 1:end_index]
    if number_str.isdigit():
        number = cast_func(number_str)
    else:
        number = int.from_bytes(base64.b85decode(number_str.encode()), signed=True)
    return number, end_index + 1


def _encode_float(data: float) -> bytes:
    if math.isinf(data):
        return b"f+e" if data > 0 else b"f-e"
    elif math.isnan(data):
        return b"f?e"
    else:
        return f"f{decimal.Decimal(str(data))}e".encode()


def _decode_float(data: str, index: int) -> tuple[float, int]:
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


def _encode_bytes(data: bytes) -> bytes:
    return f"{len(data)}:".encode() + data


def _decode_bytes(data: str, index: int) -> tuple[bytes, int]:
    colon_index = data.index(':', index)
    length = int(data[index:colon_index])
    start = colon_index + 1
    end = start + length
    return data[start:end].encode(), end


def _encode_unicode(data: str) -> bytes:
    encoded_data = data.encode()
    return f"u{len(encoded_data)}:".encode() + encoded_data


def _decode_unicode(data: str, index: int) -> tuple[str, int]:
    colon_index = data.index(':', index)
    length = int(data[index + 1:colon_index])  # Skip 'u' character
    start = colon_index + 1
    end = start + length
    decoded_str = data[start:end].encode().decode()
    return decoded_str, end


def _encode_list(data: list) -> bytes:
    if not data:
        return b"L"
    return b"l" + b"".join(encode(item) for item in data) + b"e"


def _decode_collection(data: str, index: int, type_char: str) -> tuple[list | dict | set | tuple, int]:
    if type_char in "LDST":
        return _initialize_collection(type_char), index + 1
    index += 1  # Skip the type character
    result = _initialize_collection(type_char)
    while data[index] != 'e':
        if type_char == 'd':
            key, index = _decode_bytes(data, index)
            value, index = _decode(data, index)
            result[key.decode()] = value
        else:
            item, index = _decode(data, index)
            if type_char == 's':
                result.add(item)
            else:
                result.append(item)
    return _finalize_collection(result, type_char), index + 1


def _encode_dict(data: dict) -> bytes:
    if not data:
        return b"D"
    return b"d" + b"".join(
        _encode_bytes(key.encode('utf-8')) + encode(value)
        for key, value in sorted(data.items())
    ) + b"e"


def _encode_set(data: set) -> bytes:
    if not data:
        return b"S"
    return b"s" + b"".join(encode(item) for item in sorted(data)) + b"e"


def _encode_tuple(data: tuple) -> bytes:
    if not data:
        return b"T"
    return b"t" + b"".join(encode(item) for item in data) + b"e"


def _encode_object(data: Any) -> bytes:
    import_path = f"{data.__class__.__module__}.{data.__class__.__qualname__}"
    for module_name, short_code in MODULE_MAPPING.items():
        if import_path.startswith(module_name):
            import_path = import_path.replace(module_name, short_code, 1)
            break
    attributes = {}
    if hasattr(data, '__dict__'):
        attributes.update(data.__dict__)
    if hasattr(data, '__slots__'):
        for slot in data.__slots__:
            attributes[slot] = getattr(data, slot)
    encoded_attributes = _encode_dict(attributes)
    return b"o" + _encode_unicode(import_path) + encoded_attributes


def _decode_object(data: str, index: int) -> tuple[Any, int]:
    index += 1  # Skip the 'o' character
    import_path, index = _decode_unicode(data, index)
    for short_code, module_name in REVERSE_MODULE_MAPPING.items():
        if import_path.startswith(short_code):
            import_path = import_path.replace(short_code, module_name, 1)
            break
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


def _initialize_collection(type_char: str) -> list | dict | set | tuple:
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
            raise ValueError("Invalid collection type")


def _finalize_collection(collection: list | dict | set | tuple, type_char: str) -> list | dict | set | tuple:
    if type_char == 't':
        return tuple(collection)
    return collection


def _decode_bool(data: str, index: int) -> tuple[bool, int]:
    if data[index:index + 2] == 'b1':
        return True, index + 2
    elif data[index:index + 2] == 'b0':
        return False, index + 2
    else:
        raise ValueError("Invalid boolean value")
