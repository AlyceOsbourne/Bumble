import base64
import binascii
import bz2
import functools
import gzip
import hashlib
import lzma
import zlib
from enum import Enum
from bumble.utils.abstract_codec import Codec
import heapq
from collections import Counter, namedtuple
BASE91_ALPHABET = (
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    '!#$%&()*+,./:;<=>?@[]^_`{|}~"'
)

BASE91_DICT = {c: i for i, c in enumerate(BASE91_ALPHABET)}

class Node(namedtuple("Node", ["left", "right"])):
    def walk(self, code, acc):
        self.left.walk(code, acc + "0")
        self.right.walk(code, acc + "1")

class Leaf(namedtuple("Leaf", ["char"])):
    def walk(self, code, acc):
        code[self.char] = acc or "0"

def _huffman_encode(data):
    h = []
    for ch, freq in Counter(data).items():
        h.append((freq, len(h), Leaf(ch)))
    heapq.heapify(h)
    count = len(h)
    while len(h) > 1:
        freq1, _count1, left = heapq.heappop(h)
        freq2, _count2, right = heapq.heappop(h)
        heapq.heappush(h, (freq1 + freq2, count, Node(left, right)))
        count += 1
    code = {}
    if h:
        [(_freq, _count, root)] = h
        root.walk(code, "")
    return code

def _encode(data, code):
    return "".join(code[ch] for ch in data)

def _decode(encoded_data, code):
    reverse_code = {v: k for k, v in code.items()}
    current_code = ""
    decoded_output = []
    for bit in encoded_data:
        current_code += bit
        if current_code in reverse_code:
            decoded_output.append(reverse_code[current_code])
            current_code = ""
    return bytes(decoded_output)
# Example usage
def huffman_encode(data: bytes) -> bytes:
    import bumble
    code = _huffman_encode(data)
    encoded_data = _encode(data, code)
    return bumble.encode((code, encoded_data))

def huffman_decode(data: bytes) -> bytes:
    import bumble
    code, encoded_data = bumble.decode(data)
    return _decode(encoded_data, code)


def base91_encode(data: bytes) -> bytes:
    b = 0
    nbits = 0
    out = []

    for byte in data:
        b |= byte << nbits
        nbits += 8
        if nbits > 13:
            v = b & 8191
            if v > 88:
                b >>= 13
                nbits -= 13
            else:
                v = b & 16383
                b >>= 14
                nbits -= 14
            out.append(BASE91_ALPHABET[v % 91])
            out.append(BASE91_ALPHABET[v // 91])

    if nbits:
        out.append(BASE91_ALPHABET[b % 91])
        if nbits > 7 or b > 90:
            out.append(BASE91_ALPHABET[b // 91])

    return ''.join(out).encode()


def base91_decode(data: bytes) -> bytes:
    data = data.decode()

    v = -1
    b = 0
    nbits = 0
    out = bytearray()

    for char in data:
        if char not in BASE91_DICT:
            continue
        c = BASE91_DICT[char]
        if v < 0:
            v = c
        else:
            v += c * 91
            b |= v << nbits
            if (v & 8191) > 88:
                nbits += 13
            else:
                nbits += 14
            while nbits > 7:
                out.append(b & 255)
                b >>= 8
                nbits -= 8
            v = -1

    if v + 1:
        out.append((b | v << nbits) & 255)

    return bytes(out)


def hash_encode(data: bytes, algo):
    h = hashlib.new(algo)
    h.update(data)
    return h.digest() + data


def hash_decode(data: bytes, algo, length):
    data_hash, data = data[:length], data[length:]
    h = hashlib.new(algo)
    h.update(data)
    if data_hash != h.digest():
        raise ValueError("Hash mismatch")
    return data


def null_encode(data: bytes):
    return data


def null_decode(data: bytes):
    return data


def rle_encode(data: bytes) -> bytes:
    if not data:
        return b''

    encoded = bytearray()
    prev_byte = data[0]
    count = 1

    for byte in data[1:]:
        if byte == prev_byte:
            count += 1
            if count == 256:
                encoded.extend([255, prev_byte])
                count = 1
        else:
            encoded.extend([count, prev_byte])
            prev_byte = byte
            count = 1

    encoded.extend([count, prev_byte])

    return bytes(encoded)


def rle_decode(data: bytes) -> bytes:
    if not data:
        return b''

    decoded = bytearray()
    it = iter(data)

    for count in it:
        byte = next(it)
        decoded.extend([byte] * count)

    return bytes(decoded)


def lzw_encode(data: bytes) -> list:
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    w = bytearray()
    result = []

    for byte in data:
        wc = bytes(w + bytes([byte]))
        if wc in dictionary:
            w = bytearray(wc)
        else:
            result.append(dictionary[bytes(w)])
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytearray([byte])

    if w:
        result.append(dictionary[bytes(w)])

    return result


def lzw_decode(data: list) -> bytes:
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}
    result = bytearray()
    w = bytearray([data[0]])
    result.extend(w)
    for k in data[1:]:
        if k in dictionary:
            entry = dictionary[k]
        elif k == dict_size:
            entry = w + bytes([w[0]])
        else:
            raise ValueError("Bad compressed k: %s" % k)
        result.extend(entry)
        dictionary[dict_size] = w + bytes([entry[0]])
        dict_size += 1
        w = bytearray(entry)

    return bytes(result)


class Codecs(Codec, Enum):
    AS_IS = NULL = (null_encode, null_decode)
    HEX = (binascii.hexlify, binascii.unhexlify)

    B16 = BASE16 = (base64.b16encode, base64.b16decode)
    B32 = BASE32 = (base64.b32encode, base64.b32decode)
    B64 = BASE64 = (base64.b64encode, base64.b64decode)
    B85 = BASE85 = (base64.b85encode, base64.b85decode)
    B91 = BASE91 = (base91_encode, base91_decode)

    BZ2 = (bz2.compress, bz2.decompress)
    GZ = GZIP = (gzip.compress, gzip.decompress)
    ZLIB = (zlib.compress, zlib.decompress)
    LZMA = (lzma.compress, lzma.decompress)

    SHA1 = functools.partial(hash_encode, algo='sha1'), functools.partial(hash_decode, algo='sha1', length=20)
    SHA256 = functools.partial(hash_encode, algo='sha256'), functools.partial(hash_decode, algo='sha256', length=32)
    SHA512 = functools.partial(hash_encode, algo='sha512'), functools.partial(hash_decode, algo='sha512', length=64)
    MD5 = functools.partial(hash_encode, algo='md5'), functools.partial(hash_decode, algo='md5', length=16)

    RLE = (rle_encode, rle_decode)
    HUFFMAN = (huffman_encode, huffman_decode)
    LZW = (lzw_encode, lzw_decode)


__all__ = ['Codecs']
