import json

class FormatError(Exception):
    pass


def uniq(seq):
    # https://www.peterbe.com/plog/uniqifiers-benchmark
    seen = set()
    seen_add = seen.add
    return [i for i in seq if not (i in seen or seen_add(i))]


def merge_dicts(*dicts):
    # http://stackoverflow.com/a/26853961
    merged = {}
    for d in dicts:
        merged.update(d)
    return merged


def pretty_dumps(d, float_precision=None):
    if float_precision is not None:
        # Limit number of significant digits in JSON float output.
        # See https://github.com/cambridgeltl/chat/issues/3 and
        # http://stackoverflow.com/a/1447581.
        orig_repr = json.encoder.FLOAT_REPR
        json.encoder.FLOAT_REPR = lambda o: format(o, '.{}f'.format(float_precision))

    s = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))

    if float_precision is not None:
        json.encoder.FLOAT_REPR = orig_repr

    return s
