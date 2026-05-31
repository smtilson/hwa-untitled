# Sean Update: Two bugs in this decorator:
#   1. `functools` has no `wrapper` -- you want `from functools import wraps` and
#      then `@wraps(func)` on the inner function.
#   2. The decorator line `@wrapper` references a name that is only defined on the
#      NEXT line, and the inner function is also named `wrapper` -> NameError /
#      self-shadowing. Rename the inner function (e.g. `_wrapped`).
# Also: in models.py this sits ON TOP of `@property`, so it wraps the property
# object rather than the function -- it must be property-aware or be used only on
# plain methods. As written, importing models.py (which imports check_validity)
# fails immediately.

# Windsurf: I believe this is addressed. Please document this issue was addressed
# in the reading document and update any files that reference this. then delete 
# these comments in this file.

from functools import wraps


def check_validity(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        valid, msg = self.is_valid
        if not valid:
            raise ValueError(msg)
        return func(self, *args, **kwargs)

    return wrapper
