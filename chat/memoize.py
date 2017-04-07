import json

from logging import debug

def load_json(filename):
    """Return deserialized JSON from file, or empty dictionary on error."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (IOError, ValueError):
        return {}

def save_json(data, filename):
    """Serialize JSON into file."""
    with open(filename, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=2, separators=(',', ': '))

def serializable_key(*args, **kwargs):
    """Return JSON-serializable key for given arguments."""
    if len(args) == 1 and not kwargs:
        return args[0] # simplify trivial case
    else:
        return str(args) + str(kwargs)

def persistently_memoized(filename):
    """Decorator implementing memoization with persistence to filename."""
    cache = load_json(filename)
    def decorator(func):
        def wrapper(*args, **kwargs):
            key = serializable_key(*args, **kwargs)
            if key not in cache:
                debug('cache miss: {}'.format(key))
                cache[key] = func(*args)
                save_json(cache, filename)
            else:
                debug('cache hit : {}'.format(key))
            return cache[key]
        return wrapper
    return decorator 
