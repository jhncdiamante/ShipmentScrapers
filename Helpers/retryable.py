import time


def retry_until_success(func, max_retries, delay=2, exceptions=(Exception,), name=None):
    func_name = name or getattr(func, "__name__", "anonymous_function")
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except exceptions as e:
            print(f"Attempt {attempt} failed for {func_name}")
            time.sleep(delay)
    raise Exception(f"Failed to process {func_name} after {max_retries} attempts.")


def retryable(max_retries=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return retry_until_success(
                func=lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                exceptions=exceptions,
                name=func.__name__,
            )

        return wrapper

    return decorator
