import time


def retry_until_success(func, max_retries, delay=2, exceptions=(Exception,)):
    
    for _ in range(max_retries):
        try:
            return func()
        except exceptions:
            time.sleep(delay)
    raise Exception("Failed to process function after multiple attempts.")

def retryable(max_retries=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            return retry_until_success(
                func=lambda: func(*args, **kwargs),
                max_retries=max_retries,
                delay=delay,
                exceptions=exceptions
            )
        return wrapper
    return decorator