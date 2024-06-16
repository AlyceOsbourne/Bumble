import array
import dataclasses
import enum
import functools
import itertools
import math
import operator
from types import SimpleNamespace
from typing import NamedTuple, TypedDict

import bumble
import pipeline
import standard_codecs
from descriptors import bumble as bumbled_class

# Colors for test result output
colours = {
    "Passed": "\033[92m",
    "AssertionError": "\033[91m",
    "Exception": "\033[91m"
}


@dataclasses.dataclass
class TestObject:
    a: int
    b: str
    c: float


TestNamedTuple = NamedTuple("TestNamedTuple", [("a", int), ("b", str), ("c", float)])
TestTypedDict = TypedDict("TestTypedDict", {"a": int, "b": str, "c": float})

TestEnum = enum.Enum("TestEnum", {"A": 1, "B": 2, "C": 3})
TestFlag = enum.Flag("TestFlag", {"A": 1, "B": 2, "C": 4})
TestIntEnum = enum.IntEnum("TestIntEnum", {"A": 1, "B": 2, "C": 3})
TestIntFlag = enum.IntFlag("TestIntFlag", {"A": 1, "B": 2, "C": 4})
TestStrEnum = enum.StrEnum("TestStrEnum", {"A": "a", "B": "b", "C": "c"})


@bumbled_class()
@dataclasses.dataclass(eq=True)
class TestBumbledObject:
    a: int
    b: str
    c: float


# Test cases
test_cases = [
    # Simple types
    True,
    False,
    42,
    3.14,
    b"hello",
    "hello",
    # Collections
    [1, 2, 3],
    {"key": "value"},
    {1, 2, 3},
    (1, 2, 3),
    # Complex types
    "unicode string",
    {
        'key1': 'value1',
        'key2': 42,
        'key3': ['list', 'of', 'values'],
        'key4': 3.14,
        'key5': {1, 2, 3},
        'key6': (1, 2, 3),
        'key7': 'unicode string',
        'key8': True,
        'key9': False
    },
    # Nested structures
    [1, [2, [3, [4]]]],
    {'a': {'b': {'c': 'd'}}},
    (1, (2, (3, (4,)))),
    [{'a': [1, 2, 3]}, {'b': (4, 5, 6)}],
    # Empty structures
    [],
    {},
    set(),
    tuple(),
    # Custom objects
    TestObject(1, "string", 3.14),
    TestObject(2, "another string", 6.28),
    # Mixed-type collections
    [1, "string", 3.14, True, None, b"bytes", [1, 2], {"key": "value"}],
    {"int": 42, "float": 3.14, "bool": False, "list": [1, 2],
     "dict": {"nested": "dict", 'nested_list': [1, 2, 3], 'nested_dict': {'key': 'value', 'key2': 'value2'}}},
    # Very large numbers
    10 ** 100,
    -10 ** 100,
    3.14e100,
    -3.14e100,
    # Special float values
    float('nan'),
    float('inf'),
    float('-inf'),
    # NoneType
    None,
    # Arbitrary objects
    SimpleNamespace(a=1, b={'a': 1, 'b': 2}),
    SimpleNamespace(c=[1, 2, 3], d=2.5),
    SimpleNamespace(f={1, 2, 3}, g=SimpleNamespace(h=1, i=2)),
    SimpleNamespace(j=SimpleNamespace(k=1, l=2), m=True),
    # Heavily nested structures
    SimpleNamespace(n=SimpleNamespace(o=SimpleNamespace(p=SimpleNamespace(q=SimpleNamespace(r=SimpleNamespace(
        s=SimpleNamespace(t=SimpleNamespace(u=SimpleNamespace(
            v=SimpleNamespace(w=SimpleNamespace(x=SimpleNamespace(y=SimpleNamespace(z=SimpleNamespace(a=1)))))))))))))),
    [1, [2, [3, [4, [5, [6, [7, [8, [9, [10]]]]]]]]]],
    {'a': {'b': {'c': {'d': {'e': {'f': {'g': {'h': {'i': {'j': {'k': {'l': {'m': {
        'n': {'o': {'p': {'q': {'r': {'s': {'t': {'u': {'v': {'w': {'x': {'y': {'z': {'a': 1}}}}}}}}}}}}}}}}}}}}}}}}}}},
    [[[[[[[[[[10]]]]]]]]]],
    # Arrays
    array.array('i', [1, 2, 3, 4, 5]),
    # NamedTuple
    TestNamedTuple(1, "string", 3.14),
    # TypedDict
    TestTypedDict(a=1, b="string", c=3.14),
    # Enum
    TestEnum.A,  # noqa
    TestEnum.B,  # noqa
    TestEnum.C,  # noqa
    TestFlag.A,  # noqa
    TestFlag.B,  # noqa
    TestFlag.C,  # noqa
    TestIntEnum.A,  # noqa
    TestIntEnum.B,  # noqa
    TestIntEnum.C,  # noqa
    TestIntFlag.A,  # noqa
    TestIntFlag.B,  # noqa
    TestIntFlag.C,  # noqa
    TestStrEnum.A,  # noqa
    TestStrEnum.B,  # noqa
    TestStrEnum.C,  # noqa,

]


def test_bumbled_class():
    print("Running bumbled class tests... ", end="")
    b = TestBumbledObject(1, "string", 3.14)
    encoded_data = b.__bumble__
    c = TestBumbledObject(2, "another string", 6.28)
    c.__bumble__ = encoded_data
    assert b == c, f"{colours['AssertionError']}Failed\033[0m for {b} and {c}"
    print("\r" + " " * len("Running bumbled class tests... ") + "\r", end="")


def _test(msg, encoder, decoder, **kwargs):
    print(msg, end="... ")
    for data in test_cases:
        encoded_data = encoder(data, **kwargs)
        decoded_data = decoder(encoded_data, **kwargs)
        if isinstance(data, float) and (math.isnan(data) and math.isnan(decoded_data)):
            assert True
        elif isinstance(data, float):
            assert math.isclose(data, decoded_data,
                                rel_tol=1e-9), f"{colours['AssertionError']}Failed\033[0m for {data}"
        elif isinstance(data, float) and (math.isinf(data) or math.isinf(decoded_data)):
            assert math.isinf(data) == math.isinf(decoded_data), f"{colours['AssertionError']}Failed\033[0m for {data}"
        else:
            assert data == decoded_data, f"{colours['AssertionError']}Failed\033[0m for {data}"
    print("\r" + " " * len(msg) + "\r", end="")


def test_encode_decode(**kwargs):
    _test("Running encoding/decoding tests", bumble.encode, bumble.decode, **kwargs)


def test_pipeline():
    pipeline_ = pipeline.Pipeline()
    _test("Running encoding/decoding tests with pipeline", pipeline_.encode, pipeline_.decode)


def test_pipeline_of(codec):
    pipeline_ = pipeline.Pipeline.of(codec)
    _test(f"Running encoding/decoding tests with pipeline of {codec}", pipeline_.encode, pipeline_.decode)


def test_combinations_of_pipelines(codecs=standard_codecs.Codecs, r=2):
    for item in itertools.combinations(codecs, r):
        test_pipeline_of(functools.reduce(operator.or_, item))


def test_patch():
    from bumble import pickle
    _test("Running encoding/decoding tests with monkey-patched pickle module", pickle.dumps, pickle.loads)


def main():
    test_encode_decode()
    test_pipeline()
    test_bumbled_class()

    for codec in standard_codecs.Codecs:
        test_pipeline_of(codec)

    for i in range(2, 4):
        test_combinations_of_pipelines(r=i)

    test_patch()

    print(f"{colours['Passed']}All tests passed\033[0m")


if __name__ == "__main__":
    main()
