"""Used to store things like module mappings etc."""
import sys

def generate_symbol(name, symbols):
    """Generates a unique symbol for a given name."""
    idx = 0
    symbol = f"?{name[idx]}"
    while symbol in symbols.values():
        idx += 1
        if idx >= len(name):
            raise ValueError(f"Cannot generate unique symbol for {name}")
        symbol += name[idx]
    return symbol

def map_names():
    """Tokenizes the names of the built-in and selected standard library modules."""
    builtin_names = list(sys.builtin_module_names)
    additional_names = [
        '__main__', 'collections', 'importlib', 'codecs',
        'warnings', 'traceback', 'inspect', 'functools', 'keyword', 'types',
        'abc', 'enum', 'operator', 'itertools', 'contextlib', 'collections.abc',
        'dataclasses', 'typing', 'typing_extensions', 'ast', 'dis', 'tokenize',
    ]

    names = sorted(set(builtin_names + additional_names), key=lambda x: (x, len(x)))

    symbols = {}
    for name in names:
        symbols[name] = generate_symbol(name, symbols)

    reverse_symbols = {v: k for k, v in symbols.items()}
    return symbols, reverse_symbols

MODULE_MAPPING, REVERSE_MODULE_MAPPING = map_names()
