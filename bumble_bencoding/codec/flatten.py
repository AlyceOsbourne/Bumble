from collections import defaultdict


def deflate_bytes(data: bytes) -> tuple[dict[bytes, bytes], bytes]:
    substrings = _find_repeated_subbytes(data)
    mapping = _create_mapping(substrings)

    encoded_data = _replace_subbytes(data, mapping)

    if len(data) <= len(encoded_data):
        return {}, data

    return mapping, encoded_data


def _find_repeated_subbytes(data: bytes) -> dict[bytes, int]:
    substrings = defaultdict(int)
    length = len(data)
    for size in range(2, length // 2 + 1):
        for start in range(length - size + 1):
            substring = data[start:start + size]
            substrings[substring] += 1

    substrings = {k: v for k, v in substrings.items() if v > 1}
    sorted_substrings = sorted(substrings.items(), key=lambda item: (-len(item[0]), -item[1]))

    return {k: v for k, v in sorted_substrings}


def _create_mapping(substrings: dict[bytes, int]) -> dict[bytes, bytes]:
    mapping = {}
    code = 1
    for substring in substrings:
        if all(substring not in larger for larger in mapping):
            mapping[substring] = bytes([code])
            code += 1
            if code >= 256:
                break
    return mapping


def _replace_subbytes(data: bytes, mapping: dict[bytes, bytes]) -> bytes:
    sorted_mapping = sorted(mapping.items(), key=lambda item: -len(item[0]))
    for substring, code in sorted_mapping:
        data = data.replace(substring, code)
    return data


def inflate_bytes(encoded_data: bytes, mapping: dict[bytes, bytes]) -> bytes:
    mapping = {v: k for k, v in mapping.items()}
    for code, substring in sorted(mapping.items(), key=lambda item: -len(item[1])):
        encoded_data = encoded_data.replace(code, substring)
    return encoded_data
