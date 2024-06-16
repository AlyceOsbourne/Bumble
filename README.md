# Bumble

Not as bug-filled as the title might suggest, Bumble is a superset of bencoding (pronounced Bee Encoding) that aims to be a safer, simpler alternative to Pickle. Often when pickling objects, we only care about the types and data contained, not about recreating the same objects with the same IDs. This is where many of the unsafe aspects of Pickle come from. Bumble solves this by allowing the encoding of your data without needing to encode everything about the environment or objects like code objects.

## Why Bumble Rocks:
- **Smaller Encoded Data**: Bumble's encoded data is more compact than Pickle's.
- **Safer Decoding**: Bumble does not allow the evaluation of code objects as part of its decoding process.
- **Versatile**: Fulfills most uses for Pickle, with none of the caveats.
- **Interoperable with Pickle**: You can still work with Pickle where necessary.
- **Codec Pipelines**: Full support for codec pipelines, allowing inline compression, hashing, and encryption.

**WARNING**: Bumble is still a work in progress (WIP). Many things will change over the coming days, so please, pretty please, don't write anything that will rely on this until V1 is released.

## Supported Types

Bumble can handle a wide range of types, making it extremely versatile for various data structures and objects in Python. Here's a brief overview of the types it supports:

- **Simple Types**: 
  - Boolean (`True`, `False`)
  - Integers (`42`)
  - Floats (`3.14`)
  - Bytes (`b"hello"`)
  - Strings (`"hello"`)

- **Collections**:
  - Lists (`[1, 2, 3]`)
  - Dictionaries (`{"key": "value"}`)
  - Sets (`{1, 2, 3}`)
  - Tuples (`(1, 2, 3)`)

- **Complex Types**:
  - Nested structures (`[1, [2, [3, [4]]]]`, `{'a': {'b': {'c': 'd'}}}`)
  - Mixed-type collections (`[1, "string", 3.14, True, None, b"bytes", [1, 2], {"key": "value"}]`)
  - Empty structures (`[]`, `{}`, `set()`, `tuple()`)

- **Special Values**:
  - Very large numbers (`10 ** 100`, `-10 ** 100`)
  - Special float values (`float('nan')`, `float('inf')`, `float('-inf')`)
  - `NoneType` (`None`)

- **Arbitrary Objects**:
  - Many standard library objects can be encoded and decoded.
  - As can your own created objects.

## How to Use Bumble

### Encoding and Decoding Data

Here's how you can easily convert Python objects to Bumble encoding and back again:

```python
from types import SimpleNamespace
import bumble

data = {
    'key1': 'value1',
    'key2': 42,
    'key3': [1, 2, 3],
    'key4': SimpleNamespace(a=1, b={'a': 1, 'b': 2}),
    'key5': None,
    'key6': True,
    'key7': False,
    'key8': 3.14,
    'key9': b'bytes',
    'key10': {1, 2, 3},
    'key11': (1, 2, 3),
    'key13': float('inf'),
    'key14': float('-inf'),
    'key15': 10 ** 100,
    'key16': -10 ** 100,
    'key17': {'a': {'b': {'c': 'd'}}},
    'key18': [],
    'key19': {},
    'key20': set(),
    'key21': tuple(),
    'key22': [1, "string", 3.14, True, None, b"bytes", [1, 2], {"key": "value"}],
}

encoded_data = bumble.encode(data)
print("Encoded Data:", encoded_data)

decoded_data = bumble.decode(encoded_data)
print("Decoded Data:", decoded_data)

assert data == decoded_data, "Data does not match"
```

Bumble makes it straightforward to encode and decode data while ensuring safety and efficiency. This quick example shows how seamless the process can be, providing a safer alternative to Pickle with similar versatility. 

## Incoming Features
- Pipelines, to enable you to chain multiple codecs together, allowing for compression, hashing, encryption, etc.
- Some Descriptor based tools to simplify swapping pickling for bumbling in your code.

### Note  
Bumble is intentionally designed to not support all types in order to provide a safer and simpler alternative to Pickle. It focuses on the most common types and structures.  
Bumble operates under the assumption that most users are pickling objects for their state, rather than requiring a true duplication of the object.

---
Feel free to experiment with various data types and structures to see how Bumble handles them with ease!  
If you find any issues, please let me know by raising an issue on the GitHub repository. Your feedback is invaluable in improving Bumble for everyone.