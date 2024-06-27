"""
Optimizations for Bumble Bencoding using Huffman Encoding.
"""

import heapq
from collections import Counter


def deflate_bytes(data: bytes) -> bytes:
    """Create a more optimized version of the given bytes using Huffman Encoding."""
    freq = _calculate_frequencies(data)
    huffman_tree = _build_huffman_tree(freq)
    huffman_codes = _generate_huffman_codes(huffman_tree)
    encoded_data = _encode_data(data, huffman_codes)
    return _encode_mapping(huffman_codes) + encoded_data


def inflate_bytes(encoded_data: bytes) -> bytes:
    """Restore the original bytes from the optimized version using Huffman Encoding."""
    header, data = _split_header_and_data(encoded_data)
    huffman_codes = _decode_mapping(header)
    reverse_huffman_codes = {v: k for k, v in huffman_codes.items()}
    return _decode_data(data, reverse_huffman_codes)


def _calculate_frequencies(data: bytes) -> Counter:
    """Calculate the frequency of each byte in the data."""
    return Counter(data)


def _build_huffman_tree(freq: Counter) -> list:
    """Build the Huffman Tree based on the frequencies."""
    heap = [[weight, [symbol, ""]] for symbol, weight in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        lo = heapq.heappop(heap)
        hi = heapq.heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    return heap[0]


def _generate_huffman_codes(huffman_tree: list) -> dict:
    """Generate the Huffman codes from the Huffman Tree."""
    return {symbol: code for symbol, code in huffman_tree[1:]}


def _encode_data(data: bytes, huffman_codes: dict) -> bytes:
    """Encode the data using the Huffman codes."""
    encoded_bits = ''.join(huffman_codes[byte] for byte in data)
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += '0' * padding
    padding_info = "{:08b}".format(padding)
    encoded_bits = padding_info + encoded_bits
    byte_array = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte = encoded_bits[i:i + 8]
        byte_array.append(int(byte, 2))
    return bytes(byte_array)


def _decode_data(data: bytes, reverse_huffman_codes: dict) -> bytes:
    """Decode the data using the reverse Huffman codes."""
    bit_string = ''.join(f'{byte:08b}' for byte in data)
    padding = int(bit_string[:8], 2)
    bit_string = bit_string[8:-padding]
    decoded_bytes = bytearray()
    current_bits = ''
    for bit in bit_string:
        current_bits += bit
        if current_bits in reverse_huffman_codes:
            decoded_bytes.append(reverse_huffman_codes[current_bits])
            current_bits = ''
    return bytes(decoded_bytes)


def _encode_mapping(huffman_codes: dict) -> bytes:
    """Encode the Huffman codes into a header."""
    header = bytearray()
    for symbol, code in huffman_codes.items():
        header.append(symbol)
        code_length = len(code)
        header.append(code_length)
        header.extend(int(code[i:i + 8], 2) for i in range(0, code_length, 8))
    header_length = len(header)
    return header_length.to_bytes(2) + bytes(header)


def _decode_mapping(header: bytes) -> dict:
    """Decode the Huffman codes from the header."""
    huffman_codes = {}
    index = 0
    while index < len(header):
        symbol = header[index]
        code_length = header[index + 1]
        code_bits = ''.join(f'{header[i]:08b}' for i in range(index + 2, index + 2 + (code_length + 7) // 8))
        huffman_codes[symbol] = code_bits[:code_length]
        index += 2 + (code_length + 7) // 8
    return huffman_codes


def _split_header_and_data(encoded_data: bytes) -> tuple[bytes, bytes]:
    """Split the header and the data in the encoded bytes."""
    header_length = int.from_bytes(encoded_data[:2])
    return encoded_data[2:2 + header_length], encoded_data[2 + header_length:]
