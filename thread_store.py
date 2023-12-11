import redis

thread_store = redis.Redis(decode_responses=True)


def set(key, value):
    thread_store.set(key, value)


def get(key):
    return thread_store.get(key)
