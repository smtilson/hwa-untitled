from functools import wrapper

def check_validity(func):
    @wrapper
    def wrapper(self, *args, **kwargs):
        valid, msg = self.is_valid
        if not valid:
            raise ValueError(msg)
        return func(self, *args, **kwargs)
    return wrapper