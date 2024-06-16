import dataclasses
from utils import Pipeline, EncryptedCodec, HMACCodec

@dataclasses.dataclass
class TestObject:
    a: int
    b: str
    c: float


def encode(obj, key):
    # encode to bumble encoding, then encrypt, hash, and compress
    return Pipeline.of(EncryptedCodec(key), HMACCodec(key), 'zlib').encode(obj)

def decode(data, key):
    # same as above, but in reverse
    return Pipeline.of(EncryptedCodec(key), HMACCodec(key), 'zlib').decode(data)


def test():
    obj = TestObject(42, 'hello', 3.14)
    key = 'test_key'
    encoded = encode(obj, key)
    decoded = decode(encoded, key)
    assert obj == decoded, f'{obj} != {decoded}'

    print('Passed')

test()


