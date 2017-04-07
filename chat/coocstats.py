#!/usr/bin/env python

# Generate statistics based on term co-occurrence counts.

import math

from collections import OrderedDict

from logging import warn

log = lambda x: math.log(x, 2)

class CountStats(object):
    def __init__(self, counts=None, options=None):
        """Initialize co-occurrence count statistics with given data.

        Args:
            counts: dict of dicts where counts[x][y] is the number of
            times term x co-occurs with term y, counts[x][None] and
            counts[None][y] are the number of times terms x and y
            occur standalone (resp.), and counts[None][None] is the
            total number of documents. The terms are assumed to be
            from separate vocabularies so that counts[t][None] does
            not generally equal counts[None][t].
        """
        if counts is None:
            counts = { None: { None: 0 } }    # total zero
        self._counts = counts
        self.smooth(options)
        self.measures = OrderedDict([
            ('count', self.count),
            # ('prob', self.p),
            ('cprob', self.p_y_given_x),
            ('pmi', self.pmi),
            ('npmi', self.npmi),
        ])

    def getcounts(self):
        return self._counts

    @property
    def total(self):
        return self._counts[None][None]

    def count(self, x, y):
        return 1.*self._counts[x][y]
        
    def p(self, x, y):
        return self.count(x, y) / self.total

    def p_x_given_y(self, x, y):
        return self.count(x, y) / self.count(None, y)

    def p_y_given_x(self, x, y):
        return self.count(x, y) / self.count(x, None)

    def pmi(self, x, y):
        """Return pointwise mutual information."""
        p = self.p
        if p(x, y) != 0.0:
            return log(p(x, y) / (p(x, None)*p(None, y)))
        else:
            # raise ValueError('p(%s,%s) is zero' % (x, y))
            warn('pmi: p({}, {}) is zero'.format(x, y))
            # return float('-inf')
            # TODO: Chart.js breaks for -inf, but this is hardly better.
            return -10.0

    def npmi(self, x, y):
        """Return normalized pointwise mutual information."""
        p = self.p
        if p(x, y) != 0.0:
            return log(p(x, None)*p(None, y))/log(p(x, y))-1
        else:
            return -1.0

    def smooth(self, options):
        if options and options.epsilon:
            self._counts = {
                t: { t2: v+options.epsilon for t2, v in d.items() }
                for t, d in self._counts.items()
            }

    def __iter__(self):
        """Iterate over co-occurrence data."""
        for k in self._counts:
            if k is not None:    # skip standalone counts
                yield k

    def __getitem__(self, key):
        return self._counts[key]
