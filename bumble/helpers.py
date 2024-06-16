def _initialize_collection(type_char: str) -> list | dict | set | tuple:
    """Initialize collection based on type character."""
    match type_char:
        case 'l' | 'L' | 't':
            return []
        case 'd' | 'D':
            return {}
        case 's' | 'S':
            return set()
        case 'T':
            return ()
        case _:
            raise ValueError(f"Invalid collection type: {type_char}")


def _finalize_collection(collection: list | dict | set | tuple, type_char: str) -> list | dict | set | tuple:
    """Finalize collection based on type character."""
    if type_char == 't':
        return tuple(collection)
    return collection


