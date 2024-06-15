import math
from types import SimpleNamespace
import bumble
from standard_codecs import Codecs
import itertools
import functools
import operator

# Colors for test result output
colours = {
    "Passed": "\033[92m",
    "AssertionError": "\033[91m",
    "Exception": "\033[91m"
}

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
    # Nested empty structures
    SimpleNamespace(a=SimpleNamespace(b=SimpleNamespace(c=SimpleNamespace(d=SimpleNamespace(e=SimpleNamespace(
        f=SimpleNamespace(g=SimpleNamespace(h=SimpleNamespace(i=SimpleNamespace(j=SimpleNamespace(k=SimpleNamespace(
            l=SimpleNamespace(m=SimpleNamespace(n=SimpleNamespace(o=SimpleNamespace(p=SimpleNamespace(q=SimpleNamespace(
                r=SimpleNamespace(s=SimpleNamespace(t=SimpleNamespace(u=SimpleNamespace(v=SimpleNamespace(
                    w=SimpleNamespace(
                        x=SimpleNamespace(y=SimpleNamespace(z=SimpleNamespace(a=1))))))))))))))))))))))))))),
    [[[[[[[[[[10]]]]]]]]]],
]

codecs_to_test = [
    Codecs.B64, Codecs.BZ2, Codecs.GZ, Codecs.ZLIB, Codecs.LZMA,
    Codecs.B32, Codecs.B85, Codecs.SHA256, Codecs.SHA512, Codecs.MD5
]


def run_tests(**kwargs):
    # for data in test_cases:
    #     try:
    #         encoded_data = bumble.encode(data, **kwargs)
    #         decoded_data = bumble.decode(encoded_data, **kwargs)
    #         if isinstance(data, float) and (math.isnan(data) and math.isnan(decoded_data)):
    #             assert True
    #         elif isinstance(data, float):
    #             assert math.isclose(data, decoded_data, rel_tol=1e-9), f"Failed for {data}"
    #         elif isinstance(data, float) and (math.isinf(data) or math.isinf(decoded_data)):
    #             assert math.isinf(data) == math.isinf(decoded_data), f"Failed for {data}"
    #         else:
    #             assert data == decoded_data, f"Failed for {data}"
    #         results.append((data, "Passed"))
    #     except AssertionError as e:
    #         results.append((data, f"AssertionError: {e}"))
    #     except Exception as e:
    #         results.append((data, f"Exception: {e}"))
    #
    # for data, result in results:
    #     # print(f"{colours.get(result.split(':')[0], '')}{result}\033[0m: {data}")
    #     assert result == "Passed", f"{result}: {data}"
    #     print(f"{colours.get(result.split(':')[0], '')}{result}\033[0m: {data}")

    for data in test_cases:
        encoded_data = bumble.encode(data, **kwargs)
        decoded_data = bumble.decode(encoded_data, **kwargs)
        if isinstance(data, float) and (math.isnan(data) and math.isnan(decoded_data)):
            assert True
        elif isinstance(data, float):
            assert math.isclose(data, decoded_data, rel_tol=1e-9), f"Failed for {data}"
        elif isinstance(data, float) and (math.isinf(data) or math.isinf(decoded_data)):
            assert math.isinf(data) == math.isinf(decoded_data), f"Failed for {data}"
        else:
            assert data == decoded_data, f"{colours['AssertionError']}Failed\033[0m for {data}"
    print(f"{colours['Passed']}All tests passed\033[0m")
    print()




def main():
    print("Running main tests")
    run_tests()

if __name__ == "__main__":
    main(
    )
