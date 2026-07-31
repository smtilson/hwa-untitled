"""Validity helpers shared by the model dataclasses.

``check_validity`` wraps a method/property so it raises ``ValueError`` (with the
``is_valid`` message) before running when the owning object is invalid.
"""

from functools import wraps


def check_validity(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        valid, msg = self.is_valid
        if not valid:
            raise ValueError(msg)
        return func(self, *args, **kwargs)

    return wrapper
