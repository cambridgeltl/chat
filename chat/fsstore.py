#!/usr/bin/env python

# Minimal filesystem-based store for documents with ID lookup.

import io
import json

from os import path
from operator import itemgetter
from itertools import groupby
from collections import OrderedDict

from logging import debug, warn

from common import FormatError

class FilesystemStore(object):
    """Filesystem-based store for documents with ID lookup."""

    def __init__(self, base_dir, suffix='.txt', encoding='utf-8'):
        """Initialize FilesystemStore.

        Args:
            base_dir: Path to directory with documents in subdirectories.
            suffix: Filename suffix.
        """
        self._base_dir = base_dir
        self._suffix = suffix
        self._encoding = encoding
        self._prefix_len = 4    # TODO don't hardcode

    def get(self, id_):
        """Return text of document with given ID."""
        try:
            return self._read(self._path(id_))
        except IOError:
            raise KeyError(id_)    # assume file not found (TODO)

    def _path(self, id_):
        """Return path to file with given ID."""
        # Files organized into subdirectories by ID prefix.
        data_dir = path.join(self._base_dir, id_[:self._prefix_len])
        return path.join(data_dir, id_+self._suffix)

    def _read(self, fn):
        """Return text of document with given path."""
        debug('attempting to read {}'.format(fn))
        with io.open(fn, encoding=self._encoding) as f:
            return f.read()

class PubmedStore(FilesystemStore):
    """Filesystem-based store for PubMed texts."""

    def __init__(self, base_dir, encoding='utf-8'):
        super(PubmedStore, self).__init__(base_dir, '.txt', encoding)

    def get_tiab(self, id_):
        """Return title and abstract of document with given ID."""
        text = self.get(id_)
        split = text.split('\n')
        # Remove lines containing MeSH terms or Substance annotations
        split = [s for s in split if (
            not s.startswith('MeSH Terms:\t') and
            not s.startswith('Substances:\t')
            )
        ]
        if len(split) == 1:
            title, abstract = split[0], ''
        else:
            title, abstract = split[0], '\n'.join(split[1:])
        return title, abstract

class JsonStore(FilesystemStore):
    """Filesystem-based store for JSON documents."""

    def __init__(self, base_dir, encoding='utf-8'):
        super(JsonStore, self).__init__(base_dir, '.jsonld', encoding)

    def _read(self, fn):
        """Return JSON content of document with given path."""
        debug('attempting to read {}'.format(fn))
        with open(fn) as f:
            return json.load(f)

class AnnotationStore(JsonStore):
    """Filesystem-based store for JSON annotations in WA format."""

    def __init__(self, base_dir, encoding='utf-8'):
        super(AnnotationStore, self).__init__(base_dir, encoding)

    def get_spans(self, id_, minimize=False):
        """Return text span annotations in document with given ID.

        Arguments:
            minimize: if True, eliminate duplicate and redundant
            annotations.
        """
        annotations = self.get(id_)
        spans = self.span_annotations(annotations)
        if minimize:
            spans = self.minimize_annotations(spans)
        return spans

    @staticmethod
    def minimize_annotations(annotations):
        """Return annotations without duplicate and redundant annotations."""
        minimized = []
        # Process groups sharing a target
        target = itemgetter('target')
        for _, group in groupby(sorted(annotations, key=target), key=target):
            # Eliminate duplicates sharing the same target and body
            ann_by_body, group = OrderedDict(), list(group)
            for a in group:
                if a['body'] not in ann_by_body:
                    ann_by_body[a['body']] = a
            # Eliminate redundant annotations whose bodies are superclasses
            # of other annotations.
            for a in group:
                for b in AnnotationStore.superclasses(a['body']):
                    ann_by_body.pop(b, None)
            minimized.extend(ann_by_body.values())
        return minimized

    @staticmethod
    def span_annotations(annotations):
        """Return subset of annotations with text span targets."""
        return [a for a in annotations
                if 'target' in a and 'char=' in a['target']]

    @staticmethod
    def superclasses(type_):
        """Yield known superclasses of given type."""
        # Only handle hallmark types, i.e. ones with the "hm:" prefix.
        # For hallmarks, prefixes correspond to superclasses, e.g.
        # "hm:1" and "hm:12" are superclasses of "hm:123".
        if type_.startswith('hm:'):
            super_ = type_[:-1]
            while len(super_) >= len('hm:') + 1:
                yield super_
                super_ = super_[:-1]
