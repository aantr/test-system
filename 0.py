from functools import wraps


def decorator_factory(argument):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            print(0)
            result = function(*args, **kwargs)
            return result

        return wrapper

    return decorator


@decorator_factory(1)
def func():
    print('hi')
