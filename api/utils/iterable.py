def is_iterable(obj):
    if isinstance(obj, str):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def is_iterable_of_iterables(obj):
    if not is_iterable(obj):
        return False
    return all(is_iterable(subobj) for subobj in obj)


def transform_to_iterable(obj):
    if not is_iterable(obj):
        return [obj]
    return obj


def transform_to_iterable_of_iterables(obj):
    if not is_iterable_of_iterables(obj):
        return [obj]
    return obj
