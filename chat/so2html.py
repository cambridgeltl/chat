#!/usr/bin/env python

"""Convert text and (start, end type) annotations into HTML."""

__author__ = 'Sampo Pyysalo'
__license__ = 'MIT'

import sys
import re
import unicodedata
import urlparse

from collections import namedtuple
from collections import defaultdict
from itertools import chain
from logging import warn

from namespace import expand_namespace

# the tag to use to mark annotated spans
TAG='span'

# vertical space between span boxes at different heights in pixels
# (including border)
VSPACE = 2

# text line height w/o annotations
BASE_LINE_HEIGHT = 24

# "effectively zero" height for formatting tags
EPSILON = 0.0001

Standoff = namedtuple('Standoff', 'start end type norm')

class Span(object):
    """Represents a marked span of text.

    Spans can represent either annotations or formatting. The former
    are rendered as text highligts, the latter as HTML formatting tags
    such as <i> and <p>.
    """
    def __init__(self, start, end, type_, norm=None, formatting=None):
        """Initialize annotation or formatting span.

        If formatting is None, determine whether or not this is a
        formatting tag heuristically based on type_.
        """
        self.start = start
        self.end = end
        self.type = type_
        self.norm = norm
        if formatting is not None:
            self.formatting = formatting
        else:
            self.formatting = is_formatting_type(self.type)

        self.nested = set()
        self._height = None

        self.start_marker = None

        # generate link (<a> tag) with given href if not None
        self.href = None

    def tag(self):
        """Return HTML tag to use to render this marker."""
        # Formatting tags render into HTML tags according to a custom
        # mapping. Other tags with href render into links (<a>) unless
        # they nest other spans (nested links are illegal, see
        # http://www.w3.org/TR/html401/struct/links.html#h-12.2.2),
        # and the remaining into the generic TAG.
        if not self.formatting:
            if self.href is not None and self.height() == 0:
                return 'a'
            else:
                return TAG
        else:
            return type_to_formatting_tag(self.type)

    def markup_type(self):
        """Return a coarse variant of the type that can be used as a label in
        HTML markup (tag, CSS class name, etc)."""
        return html_safe_string(coarse_type(self.type))

    def sort_height(self):
        """Relative height of this tag for sorting purposes."""
        # For the purposes of sorting, count the height of formatting
        # tags similarly to other tags, adding a very small value,
        # EPSILON, to give correct sort order.
        if not self.formatting:
            return self.height()
        else:
            # This +1 compensates for the lack of own height in height()
            return self.height() + 1 + EPSILON

    def height(self):
        """Relative height of this tag (except for sorting)."""
        # Formatting tags have effectively zero height, i.e. they
        # should not affect the height of tags that wrap them. TODO:
        # this still leaves a height+1 effect when a formatting tag is
        # the only one nested by a regular one; fix this.
        ownh = 1 if not self.formatting else 0
        if self._height is None:
            if not self.nested:
                self._height = 0
            else:
                self._height = max([n.height() for n in self.nested]) + ownh
        return self._height

# Span type to HTML tag mapping for formatting spans. Note that these
# are URIs we came up with and not likely to be adopted by many tools
# (see e.g. https://github.com/spyysalo/knowtator2oa/issues/1).
FORMATTING_TYPE_TAG_MAP = {
    'http://www.w3.org/TR/html/#b': 'b',
    'http://www.w3.org/TR/html/#i': 'i',
    'http://www.w3.org/TR/html/#u': 'u',
    'http://www.w3.org/TR/html/#h1': 'h1',
    'http://www.w3.org/TR/html/#sup': 'sup',
    'http://www.w3.org/TR/html/#sub': 'sub',
    'http://purl.obolibrary.org/obo/IAO_0000314': 'section',
    # forms used in initial CRAFT RDFization
    'http://craft.ucdenver.edu/iao/bold': 'b',
    'http://craft.ucdenver.edu/iao/italic': 'i',
    'http://craft.ucdenver.edu/iao/underline': 'u',
    'http://craft.ucdenver.edu/iao/sub': 'sub',
    'http://craft.ucdenver.edu/iao/sup': 'sup',
}

def is_formatting_type(type_):
    """Return True if the given type can be assumed to identify a
    formatting tag such as bold or italic, False otherwise."""
    return type_ in FORMATTING_TYPE_TAG_MAP

def type_to_formatting_tag(type_):
    """Return the HTML tag corresponding to the given formatting type."""
    tag = FORMATTING_TYPE_TAG_MAP.get(type_, type_)
    return html_safe_string(tag) # just in case

class Marker(object):
    def __init__(self, span, offset, is_end, cont_left=False, 
                 cont_right=False):
        self.span = span
        self.offset = offset
        self.is_end = is_end
        self.cont_left = cont_left
        self.cont_right = cont_right

        self.covered_left = False
        self.covered_right = False

        # at identical offsets, ending markers sort highest-last,
        # starting markers highest-first.
        self.sort_idx = self.span.sort_height() * (1 if self.is_end else -1)

        # store current start marker in span to allow ending markers
        # to affect tag style
        if not is_end:
            self.span.start_marker = self

        # attributes in generated HTML
        self._attributes = defaultdict(list)

    def add_attribute(self, name, value):
        self._attributes[name].append(value)

    def get_attributes(self):
        return sorted([(k, ' '.join(v)) for k, v in self._attributes.items()])

    def attribute_string(self):
        return ' '.join('%s="%s"' % (k, v) for k, v in self.get_attributes())

    def fill_style_attributes(self):
        self.add_attribute('class', 'ann')
        self.add_attribute('class', 'ann-h%d' % self.span.height())
        self.add_attribute('class', 'ann-t%s' % self.span.markup_type())
        # TODO: this will produce redundant class combinations in
        # cases (e.g. "continueleft openleft")
        if self.cont_left:
            self.add_attribute('class', 'ann-contleft')
        if self.cont_right:
            self.add_attribute('class', 'ann-conright')
        if self.covered_left:
            self.add_attribute('class', 'ann-openleft')
        if self.covered_right:
            self.add_attribute('class', 'ann-openright')

    def __unicode__(self):
        if self.is_end:
            return u'</%s>' % self.span.tag()
        elif self.span.formatting:
            # Formatting tags take no style
            return u'<%s>' % self.span.tag()
        else:
            self.fill_style_attributes()
            attributes = self.attribute_string()
            return u'<%s %s>' % (self.span.tag(), attributes)

def marker_sort(a, b):
    return cmp(a.offset, b.offset) or cmp(a.sort_idx, b.sort_idx)

def leftmost_sort(a, b):
    c = cmp(a.start, b.start)
    return c if c else cmp(b.end-b.start, a.end-a.start)    

def longest_sort(a, b):
    c = cmp(b.end-b.start, a.end-a.start)
    return c if c else cmp(a.start, b.start)

def resolve_heights(spans):
    # algorithm for determining visualized span height:

    # 1) define strict total order of spans (i.e. for each pair of
    # spans a, b, either a < b or b < a, with standard properties for
    # "<")

    # 2) traverse spans leftmost-first, keeping list of open spans,
    # and for each span, sort open spans in defined order and add
    # later spans to "nested" collections of each earlier span (NOTE:
    # this step is simple, but highly sub-optimal)

    # 3) resolve height as 0 for spans with no nested spans and
    # max(height(n)+1) for n in nested for others.

    open_span = []
    for s in sorted(spans, leftmost_sort):
        open_span = [o for o in open_span if o.end > s.start]
        open_span.append(s)
        # TODO: use a sorted container instead.
        open_span.sort(longest_sort)

        # WARNING: O(n^3) worst case!
        # TODO: I think that only spans just before and just after the
        # inserted span can have meaningful changes in their "nested"
        # collections. Ignore others.
        for i in range(len(open_span)):
            for j in range(i+1, len(open_span)):
                open_span[i].nested.add(open_span[j])

    return max(s.height() for s in spans) if spans else -1

LEGEND_CSS=""".legend {
  float:right;
  margin: 20px;
  border: 1px solid gray;
  font-size: 90%;
  background-color: #eee;
  padding: 10px;
  border-radius:         6px;
  -moz-border-radius:    6px;
  -webkit-border-radius: 6px;
  box-shadow: 0 5px 10px         rgba(0, 0, 0, 0.2);
  -moz-box-shadow: 0 5px 10px    rgba(0, 0, 0, 0.2);
  -webkit-box-shadow: 0 5px 10px rgba(0, 0, 0, 0.2);
  line-height: normal;
  font-family: sans-serif;
}
.legend span {
  display: block;
  padding: 2px;
  margin: 2px;
}
.clearfix { /* from bootstrap, to avoid legend overflow */
  *zoom: 1;
}
.clearfix:before,
.clearfix:after {
  display: table;
  line-height: 0;
  content: "";
}
.clearfix:after {
  clear: both;
}"""

BASE_CSS=""".ann {
  border: 1px solid gray;
  background-color: lightgray;
  border-radius:         3px;
  -moz-border-radius:    3px;
  -webkit-border-radius: 3px;
}
.ann-openright {
  border-right: none;
}
.ann-openleft {
  border-left: none;
}
.ann-contright {
  border-right: none;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}
.ann-contleft {
  border-left: none;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}"""

def line_height_css(height):
    if height == 0:
        return ''
    else:
        return 'line-height: %dpx;\n' % (BASE_LINE_HEIGHT+2*height*VSPACE)

def generate_css(max_height, color_map, legend):
    css = [LEGEND_CSS] if legend else []
    css.append(BASE_CSS)
    for i in range(max_height+1):
        css.append(""".ann-h%d {
  padding-top: %dpx;
  padding-bottom: %dpx;
  %s
}""" % (i, i*VSPACE, i*VSPACE, line_height_css(i)))
    for t, c in color_map.items():
        css.append(""".ann-t%s {
  background-color: %s;
  border-color: %s;
}""" % (html_safe_string(t), c, darker_color(c)))
    return '\n'.join(css)

def uniq(s):
    """Return unique items in given sequence, preserving order."""
    # http://stackoverflow.com/a/480227
    seen = set()
    return [ i for i in s if i not in seen and not seen.add(i)]

def generate_legend(types, colors):
    parts = ['''<div class="legend">Legend<table>''']
    for f, c in zip(types, colors):
        t = html_safe_string(f)
        tagl, tagr = '<%s class="ann ann-t%s">' % (TAG, t), '</%s>' % TAG
        parts.append('<tr><td>%s%s%s</td></tr>' % (tagl, f, tagr))
    parts.append('</table></div>')
    return ''.join(parts)

# Mapping from known ontology ID prefixes to coarse human-readable types.
# (These are mostly CRAFT strings at the moment.)
prefix_to_coarse_type = {
    'http://www.ncbi.nlm.nih.gov/taxonomy/': 'taxonomy',
    'http://purl.obolibrary.org/obo/GO_': 'Gene Ontology',
    'http://purl.obolibrary.org/obo/SO_': 'Sequence Ontology',
    'http://purl.obolibrary.org/obo/PR_': 'Protein Ontology',
    'http://www.ncbi.nlm.nih.gov/gene/': 'NCBI Gene',
    'http://purl.obolibrary.org/obo/CHEBI_': 'ChEBI',
    'http://purl.obolibrary.org/obo/NCBITaxon_': 'NCBI Taxon',
    'http://purl.obolibrary.org/obo/CL_': 'Cell Ontology',
    'http://purl.obolibrary.org/obo/BFO_': 'Basic Formal Ontology',
    'http://purl.obolibrary.org/obo/DOID_': 'Disease Ontology',
    'http://purl.obolibrary.org/obo/BTO_': 'BRENDA Tissue Ontology',
    'http://purl.obolibrary.org/obo/NCBITaxon_taxonomic_rank': 'Rank',
    'http://purl.obolibrary.org/obo/NCBITaxon_species': 'Species',
    'http://purl.obolibrary.org/obo/NCBITaxon_subspecies': 'Subspecies',
    'http://purl.obolibrary.org/obo/NCBITaxon_phylum': 'Phylym',
    'http://purl.obolibrary.org/obo/NCBITaxon_kingdom': 'Kingdom',
    'http://purl.obolibrary.org/obo/IAO_0000314': 'section',
    # STRING and STITCH DBs
    'http://string-db.org/interactions/': 'stringdb',
    'http://stitchdb-db.org/interactions/': 'stitchdb',
    # LION/CHAT
    'hm:1': 'Activating invasion and metastasis',
    'hm:2': 'Avoiding immune destruction',
    'hm:3': 'Deregulating cellular energetics',
    'hm:4': 'Enabling replicative immortality',
    'hm:5': 'Evading growth suppressors',
    'hm:6': 'Genome instability and mutation',
    'hm:7': 'Inducing angiogenesis',
    'hm:8': 'Resisting cell death',
    'hm:9': 'Sustaining proliferative signaling',
    # a and x are alternative labels here
    'hm:a': 'Tumor promoting inflammation',
    'hm:x': 'Tumor promoting inflammation',
}

def coarse_type(type_):
    """Return short, coarse, human-readable type for given type.

    For example, for "http://purl.obolibrary.org/obo/SO_0000704 return
    e.g. "Sequence Ontology".
    """
    # TODO: consider caching

    # Known mappings
    for prefix, value in prefix_to_coarse_type.iteritems():
        if type_.startswith(prefix):
            return value

    # Not known, apply heuristics. TODO: these are pretty crude and
    # probably won't generalize well. Implement more general approach.

    # start: body e.g. http://purl.obolibrary.org/obo/BFO_000000
    try:
        parsed = urlparse.urlparse(type_)
        type_str = parsed.path
    except Exception, e:
        type_str = type_
    parts = type_str.strip('/').split('/')

    # split path: parts e.g. ['obo', 'SO_0000704'] or ['gene', '15139']
    if len(parts) > 1 and parts[-2] == 'obo':
        return parts[-1].split('_')[0]
    elif parts[0] == 'gene':
        return parts[0]
    return type_str.strip('/').split('/')[-1]

def _add_formatting_spans(spans, text):
    """Add formatting spans based on text."""
    # Skip if there are any formatting types in the user-provided data
    # on the assumption that users able to do formatting will want
    # full control.
    if any(s for s in spans if is_formatting_type(s.type)):
        return spans

    # Add sections based on newlines in the text
    offset = 0
    section = 'http://purl.obolibrary.org/obo/IAO_0000314'
    for s in re.split('(\n)', text):
        if s and not s.isspace():
            spans.append(Span(offset, offset+len(s), section, formatting=True))
        offset += len(s)

    return spans

def _filter_empty_spans(spans):
    filtered = []
    for span in spans:
        if span.start == span.end:
            warn('ignoring empty span')
        else:
            filtered.append(span)
    return filtered

def _standoff_to_html(text, standoffs, legend, tooltips, links):
    """standoff_to_html() implementation, don't invoke directly."""

    # Convert standoffs to Span objects.
    spans = [Span(so.start, so.end, so.type, so.norm) for so in standoffs]

    # Add formatting such as paragraph breaks if none are provided.
    spans = _add_formatting_spans(spans, text)

    # Filter out empty spans (not currently supported)
    spans = _filter_empty_spans(spans)

    # Generate mapping from detailed to coarse types. Coarse types
    # group detailed types for purposes of assigning display colors
    # etc.
    types = uniq(s.type for s in spans if not s.formatting)
    type_to_coarse = { t: coarse_type(t) for t in types }
    coarse_types = uniq(type_to_coarse.values())

    # Pick a color for each coarse type.
    types = uniq(s.type for s in spans if not s.formatting)
    colors = span_colors(coarse_types)
    color_map = dict(zip(coarse_types, colors))

    # generate legend if requested
    if not legend:
        legend_html = ''
    else:
#         full_forms = uniq(so.type for so in standoffs)
#         type_to_full_form = { html_safe_string(f) : f for f in full_forms }
#         legend_types = [ type_to_full_form[t] for t in types ]
        legend_html = generate_legend(coarse_types, colors)

    # resolve height of each span by determining span nesting
    max_height = resolve_heights(spans)

    # Generate CSS as combination of boilerplate and height-specific
    # styles up to the required maximum height.
    css = generate_css(max_height, color_map, legend)

    # Decompose into separate start and end markers for conversion
    # into tags.
    markers = []
    for s in spans:
        markers.append(Marker(s, s.start, False))
        markers.append(Marker(s, s.end, True))
    markers.sort(marker_sort)
    
    # process markers to generate additional start and end markers for
    # instances where naively generated spans would cross.
    i, o, out = 0, 0, []
    open_span = set()
    while i < len(markers):        
        if o != markers[i].offset:
            out.append(text[o:markers[i].offset])
        o = markers[i].offset
        
        # collect markers opening or closing at this position and
        # determine max opening/closing marker height
        to_open, to_close = [], []
        max_change_height = -1
        last = None
        for j in range(i, len(markers)):
            if markers[j].offset != o:
                break
            if markers[j].is_end:
                to_close.append(markers[j])
            else:
                to_open.append(markers[j])
            max_change_height = max(max_change_height, markers[j].span.height())
            last = j

        # open spans of height < max_change_height must close to avoid
        # crossing tags; add also to spans to open to re-open and
        # make note of lowest "covered" depth.
        min_cover_height = float('inf') # TODO
        for s in open_span:
            if s.height() < max_change_height and s.end != o:
                s.start_marker.cont_right = True
                to_open.append(Marker(s, o, False, True))
                to_close.append(Marker(s, o, True))
                min_cover_height = min(min_cover_height, s.height())

        # mark any tags behind covering ones so that they will be
        # drawn without the crossing border
        for m in to_open:
            if m.span.height() > min_cover_height:
                m.covered_left = True
        for m in to_close:
            if m.span.height() > min_cover_height:
                m.span.start_marker.covered_right = True

        # reorder (note: might be unnecessary in cases; in particular,
        # close tags will typically be identical, so only their number
        # matters)
        to_open.sort(marker_sort)
        to_close.sort(marker_sort)

        # add tags to stream
        for m in to_close:
            out.append(m)
            open_span.remove(m.span)
        for m in to_open:
            out.append(m)
            open_span.add(m.span)
                
        i = last+1
    out.append(text[o:])

    if legend_html:
        out = [legend_html] + out

    # add in attributes to trigger tooltip display
    if tooltips:
        for m in (o for o in out if isinstance(o, Marker) and not o.is_end):
            m.add_attribute('class', 'hint--top')
            # TODO: useful, not renundant info
            m.add_attribute('data-hint', m.span.type)

    # add in links for spans with HTML types if requested
    if links:
        for m in (o for o in out if isinstance(o, Marker) and not o.is_end):
            href = expand_namespace(m.span.norm) if m.span.norm else None
            if href and 'http://' in href:    # TODO better heuristics
                m.span.href = href
                m.add_attribute('href', href)
                m.add_attribute('target', '_blank')

    return css, u''.join(unicode(o) for o in out)

def darker_color(c, amount=0.3):
    """Given HTML-style #RRGGBB color string, return variant that is
    darker by the given amount."""

    import colorsys

    if c and c[0] == '#':
        c = c[1:]
    if len(c) != 6:
        raise ValueError
    r, g, b = map(lambda h: int(h, 16)/255., [c[0:2],c[2:4],c[4:6]])
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    v *= 1.0-amount
    r, g, b = [255*x for x in colorsys.hsv_to_rgb(h, s, v)]
    return '#%02x%02x%02x' % (r, g, b)

def random_colors(n, seed=None):
    import random
    import colorsys
    
    random.seed(seed)
    
    # based on http://stackoverflow.com/a/470747
    colors = []
    for i in range(n):
        hsv = (1.*i/n, 0.9 + random.random()/10, 0.9 + random.random()/10)
        rgb = tuple(255*x for x in colorsys.hsv_to_rgb(*hsv))
        colors.append('#%02x%02x%02x' % rgb)
    return colors

# Kelly's high-contrast colors [K Kelly, Color Eng., 3 (6) (1965)],
# via http://stackoverflow.com/a/4382138. Changes: black excluded as
# not applicable here, plus some reordering (numbers in comments give
# original order).
kelly_colors = [
#     '#000000', #  2 black
    '#FFB300', #  3 yellow
    '#007D34', # 10 green
    '#FF6800', #  5 orange
    '#A6BDD7', #  6 light blue
    '#C10020', #  7 red
    '#CEA262', #  8 buff
    '#817066', #  9 gray
#     '#FFFFFF', #  1 white
    '#803E75', #  4 purple
    '#F6768E', # 11 purplish pink
    '#00538A', # 12 blue
    '#FF7A5C', # 13 yellowish pink
    '#53377A', # 14 violet
    '#FF8E00', # 15 orange yellow
    '#B32851', # 16 purplish red
    '#F4C800', # 17 greenish yellow
    '#7F180D', # 18 reddish brown
    '#93AA00', # 19 yellow green
    '#593315', # 20 yellowish brown
    '#F13A13', # 21 reddish orange
    '#232C16', # 22 olive green
]

# Pre-set colors
type_color_map = {
    'Organism_subdivision':    '#ddaaaa',
    'Anatomical_system':       '#ee99cc',
    'Organ':                   '#ff95ee',
    'Multi-tissue_structure':  '#e999ff',
    'Tissue':                  '#cf9fff',
    'Developing_anatomical_structure': '#ff9fff',
    'Cell':                    '#cf9fff',
    'Cellular_component':      '#bbc3ff',
    'Organism_substance':      '#ffeee0',
    'Immaterial_anatomical_entity':    '#fff9f9',
    'Pathological_formation':  '#aaaaaa',
    'Cancer':  '#999999',
    'Gene': '#7fa2ff',
    'Chemical': '#8fcfff',
    'Species': '#ffccaa',
    'Disease': '#aaaaaa',
}

def span_colors(types):
    missing = [t for t in types if t not in type_color_map]
    if len(missing) <= len(kelly_colors):
        fill = kelly_colors[:len(missing)]
    else:
        fill = random_colors(len(missing), 1)
    colors = []
    i = 0
    for t in types:
        if t in type_color_map:
            colors.append(type_color_map[t])
        else:
            colors.append(fill[i])
            i += 1
    return colors

# exceptions for html_safe_string
_html_safe_map = {
    '(': u'LEFT-PAREN',
    ')': u'RIGHT-PAREN',
}

def html_safe_string(s, encoding='utf-8'):
    """Given a non-empty string, return a variant that can be used as
    a label in HTML markup (tag, CSS class name, etc)."""

    # TODO: consider caching
    if not s or s.isspace():
        raise ValueError('empty string "%s"' % s)

    if isinstance(s, unicode):
        c = s
    else:
        c = s.decode(encoding)

    # specific exceptions
    c = _html_safe_map.get(c, c)

    # adapted from http://stackoverflow.com/q/5574042
    c = unicodedata.normalize('NFKD', c).encode('ascii', 'ignore')
    c = re.sub(r'[^_a-zA-Z0-9-]', '-', c)
    c = re.sub(r'--+', '-', c)
    c = c.strip('-')

    if c and c[0].isdigit():
        c = '_' + c

    if len(c) == 0:
        c = 'NON-STRING-TYPE'

    # Sanity check from http://stackoverflow.com/a/449000, see also
    # http://www.w3.org/TR/CSS21/grammar.html#scanner
    assert re.match(r'^-?[_a-zA-Z]+[_a-zA-Z0-9-]*', c), \
        'Internal error: failed to normalize "%s"' % s

    return c

def _header_html(css, links):
    return """<!DOCTYPE html>
<html>
<head>
%s
<style type="text/css">
html {
  background-color: #eee;
  font-family: sans;
}
body {
  background-color: #fff;
  border: 1px solid #ddd;
  padding: 15px; margin: 15px;
  line-height: %dpx
}
section {
  padding: 5px;
}
%s
/* This is a hack to correct for hint.css making blocks too high. */
.hint, [data-hint] { display: inline; }
/* Block linking from affecting styling */
a.ann {
  text-decoration: none;
  color: inherit;
}
</style>
</head>
<body class="clearfix">""" % (links, BASE_LINE_HEIGHT, css)

def _trailer_html():
    return """</body>
</html>"""

# priority order of keys in structured bodies to select as types for
# visualization.
_key_priority_as_type = [
    'id',
    'label',
]

def _to_standoff_type(value):
    """Convert OA body value to type for visualization."""
    if isinstance(value, dict):
        for key in _key_priority_as_type:
            if key in value:
                # TODO: don't just discard possible other items in dict
                return value[key]
        # Just pick the first key in default sort order
        return value[sorted(value.keys())[0]]
    else:
        # TODO: cover other options also
        return str(value)

def _parse_body(annotation):
    """Return list of (types, url) for given OA annotation body."""
    try:
        body = annotation['body']
    except KeyError:
        return [('<unknown>', None)]
    if isinstance(body, basestring):
        return [(body, body)]
    elif isinstance(body, list):
        return [(_to_standoff_type(item), item) for item in body]
    else:
        return [(_to_standoff_type(body), _to_standoff_type(body))]

def oa_to_standoff(annotations, target_key='target'):
    """Convert OA annotations to Standoff objects."""
    standoffs = []
    for annotation in annotations:
        target = annotation[target_key]
        # assume target is current doc, ignore all but fragment.
        fragment = urlparse.urldefrag(target)[1]
        try:
            start_end = fragment.split('=', 1)[1]
            start, end = start_end.split(',')
        except IndexError:
            warn('failed to parse target %s' % target)
            start, end = 0, 1
        for type_, norm in _parse_body(annotation):
            standoffs.append(Standoff(int(start), int(end), type_, norm))
    return standoffs

def standoff_to_html(text, annotations, legend=True, tooltips=False,
                     links=False, content_only=False, oa_annotations=True):
    """Create HTML representation of given text and annotations.
    """
    if oa_annotations:
        annotations = oa_to_standoff(annotations)

    css, body = _standoff_to_html(text, annotations, legend, tooltips, links)

    if content_only:
        # Skip header, trailer and CSS for embedding
        return body

    # Note: tooltips are not generated by default because their use
    # depends on the external CSS library hint.css and this script
    # aims to be standalone in its basic application.
    if not tooltips:
        links_string = ''
    else:
        links_string = '<link rel="stylesheet" href="static/css/hint.css">'

    return (_header_html(css, links_string) + body +  _trailer_html())
