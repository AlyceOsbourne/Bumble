import base64
import binascii
import bz2
import functools
import gzip
import hashlib
import lzma
import zlib
from enum import Enum
from heapq import heappush, heappop, heapify
from collections import defaultdict

# Placeholder for the Codec class which should be defined in the utils.abstract_codec module.
# Assuming Codec is an abstract base class for codec implementations.
from utils.abstract_codec import Codec


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
            # If count exceeds 255, split the run
            if count == 256:
                encoded.extend([255, prev_byte])
                count = 1
        else:
            encoded.extend([count, prev_byte])
            prev_byte = byte
            count = 1

    # Add the last run
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

# LZW helper functions
def lzw_encode(data: bytes) -> list:
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    w = bytearray()
    result = []

    for byte in data:
        wc = bytes(w + bytes([byte]))  # Convert to bytes
        if wc in dictionary:
            w = bytearray(wc)  # Convert back to bytearray
        else:
            result.append(dictionary[bytes(w)])  # Convert to bytes
            dictionary[wc] = dict_size
            dict_size += 1
            w = bytearray([byte])

    if w:
        result.append(dictionary[bytes(w)])  # Convert to bytes

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
    B64 = (base64.b64encode, base64.b64decode)
    HEX = (binascii.hexlify, binascii.unhexlify)
    BZ2 = (bz2.compress, bz2.decompress)
    GZ = (gzip.compress, gzip.decompress)
    ZLIB = (zlib.compress, zlib.decompress)
    LZMA = (lzma.compress, lzma.decompress)
    B32 = (base64.b32encode, base64.b32decode)
    B85 = (base64.b85encode, base64.b85decode)

    SHA1 = functools.partial(hash_encode, algo='sha1'), functools.partial(hash_decode, algo='sha1', length=20)
    SHA256 = functools.partial(hash_encode, algo='sha256'), functools.partial(hash_decode, algo='sha256', length=32)
    SHA512 = functools.partial(hash_encode, algo='sha512'), functools.partial(hash_decode, algo='sha512', length=64)
    MD5 = functools.partial(hash_encode, algo='md5'), functools.partial(hash_decode, algo='md5', length=16)

    RLE = (rle_encode, rle_decode)
    LZW = (lzw_encode, lzw_decode)


__all__ = ['Codecs']
