"""Used to store things like module mappings etc."""
import sys


def map_names():
    """Tokenizes the names of the built-in modules."""
    # TODO: Check how this behaves across different versions of Python.
    #  We may need to serialize pythons version, and use that to determine the module names.
    names = sorted(list(sys.builtin_module_names))
    symbols = {
        '__main__': '?M',
    }
    for name in names:
        idx = 0
        symbol = f"?{name[idx]}"
        while symbol in symbols.values():
            idx += 1
            symbol += name[idx]
        symbols[name] = symbol
    return symbols, {v: k for k, v in symbols.items()}


MODULE_MAPPING, REVERSE_MODULE_MAPPING = map_names()
