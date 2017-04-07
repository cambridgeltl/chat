import json

from collections import OrderedDict

from logging import debug

from flask import request, render_template, Markup, Response, abort

from coocstats import CountStats
from charts import chart_types
from hocqueries import hocqueries
from examples import example_terms, example_pairs
from common import uniq, merge_dicts, pretty_dumps

from chat import pubmed_text_store, pubmed_ann_store
from chat import db_controller
from chat import app

from significance import term_significance
from hallmarks import hallmark_codes, top_hallmark_codes
from legends import get_legend

from config import DEFAULT_CHART, DEFAULT_MEASURE, DEBUG, DEVEL
from charts import POS_ONLY, POS_LEFT, POS_RIGHT


@app.errorhandler(Exception)
def catchall_exception_handler(e):
    import traceback
    try:
        trace = traceback.format_exc()
    except:
        trace = '(no traceback)'
    if DEVEL:
        msg = '<html><pre>{}</pre></html>'.format(trace)
    else:
        msg = 'Application error'
    return msg, 500


### Static views


@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/api')
def api():
    args = { 'root': '/' }    # TODO don't hardcode app root
    return render_template('api.html', **args)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hallmarks')
def hallmarks():
    return render_template('hallmarks.html')


### Dynamic views


@app.route('/')
@app.route('/index')
def index():
    terms = get_query_terms()
    if not terms:
        return generate_index()
    else:
        return generate_charts(terms, measure=getarg('measure'),
                               chart_type=getarg('chart_type'))

@app.route('/compare')
def compare():
    terms = uniq(get_query_terms())
    template_args = { 'compare' : True, 'tabindex': 1 }
    if not terms:
        return generate_index(template_args)
    elif len(terms) < 2:
        messages = { 'errors': [ 'Please provide two different query terms' ] }
        return generate_index(merge_dicts(template_args, messages))
    else:
        terms = terms[:2]    # Ignore extra terms
        return generate_comparison(terms, measure=getarg('measure'))

@app.route('/pubmed/<id_>')
def pubmed(id_):
    from so2html import standoff_to_html
    from operator import itemgetter
    from itertools import groupby

    try:
        text = '\n'.join(pubmed_text_store.get_tiab(id_))
    except KeyError:
        abort(404)
    try:
        ann = pubmed_ann_store.get_spans(id_, minimize=True)
    except KeyError:
        # Assume no annotations.
        ann = []

    html = standoff_to_html(text, ann, legend=True, tooltips=True,
                            links=False, content_only=True)
    template_args = { 'documents': { id_: { 'html': Markup(html), } } }
    return render_template_with_globals('pubmed.html', template_args)

@app.route('/pubmed/<id_>/text')
def pubmed_text(id_):
    try:
        return '\n'.join(pubmed_text_store.get_tiab(id_))
    except KeyError:
        abort(404)

@app.route('/pubmed/<id_>/annotations')
def pubmed_annotations(id_):
    return pretty_dumps(pubmed_ann_store.get_spans(id_, minimize=True))

@app.route('/search')
def search():
    terms, hallmarks = get_query_terms(), get_hallmark_terms()
    results = db_controller.searchTextAndHallmarks(terms[0], hallmarks, 100)
    if not results:
        return 'No results for {}'.format(terms)    # TODO
    # Add PMID based on sentence ID. By convention, sentence IDs are
    # of the form <PMID>-<SENTIDX>.
    for r in results:
        r['pmid'] = r['id'].split('-')[0]
    # Add title text by looking up document text.
    for r in results:
        try:
            r['title'] = pubmed_text_store.get(r['pmid']).split('\n')[0]
        except KeyError:
            # Document missing. TODO: better resolution?
            r['title'] = ''
    template_args = { 'results': results }
    return render_template_with_globals('searchresult.html', template_args)

@app.route('/chartdata')
def chart_data():
    # TODO: eliminate duplication with generate_charts()
    terms = get_query_terms()
    if not terms:
        return 'No query terms'
    measure = getarg('measure')
    hallmarks = getarg('hallmarks', 'top')
    hallmark_filter = top_hallmark_codes if hallmarks == 'top' else None

    stats = hallmark_cooccurrences(terms, hallmark_filter)
    m = select_measure(stats, measure)
    measure_name = selected_measure(stats, measure)

    def fmt(v):
        """Format measure value as string."""
        if isinstance(v, int) or float(v).is_integer():
            return str(int(v))
        else:
            return '{:.4f}'.format(v)

    fields = []
    for term in terms:
        fields.append((term, measure_name))
        term_total = int(stats.count(term, None))
        values = [
            (hm, fmt(m(term, hm))) for hm in stats[term] if hm is not None
        ]
        fields.extend(values)
        fields.append([])
    return Response(
        response='\n'.join('\t'.join(f) for f in fields),
        status=200,
        mimetype="text/plain",    # TODO make parameter?
    )

def getarg(arg, default=None):
    return request.args.get(arg, default)

def get_query_terms():
    from config import QUERY_PARAMETER as q
    return [ t for t in request.args.getlist(q) if t and not t.isspace() ]

def get_hallmark_terms():
    from config import HALLMARK_PARAMETER as h
    return [ t for t in request.args.getlist(h) if t and not t.isspace() ]

def hidden_parameters(terms):
    """Return hidden HTML form input fields including the given terms."""
    from config import QUERY_PARAMETER as q
    return Markup('\n'.join(
        '<input type="hidden" name="{}" value="{}">'.format(q, t)
        for t in terms
    ))

def selected_measure(stats, name):
    return name if name in stats.measures else  DEFAULT_MEASURE

def select_measure(stats, name):
    return stats.measures.get(name, stats.measures[DEFAULT_MEASURE])

def select_chart(chart_type):
    return chart_types.get(chart_type, chart_types[DEFAULT_CHART])

def generate_index(template_args=None):
    if template_args is None:
        template_args = {}
    template_args['term_examples'] = example_terms
    template_args['comparison_examples'] = example_pairs
    return render_template_with_globals('index.html', template_args)

def filter_cooccurrence_data(data, hallmark_filter):
    filtered = OrderedDict()
    for term in data:
        filtered[term] = OrderedDict()
        for hm in data[term]:
            if hm is not None and hm not in hallmark_filter:
                continue
            filtered[term][hm] = data[term][hm]
    return filtered

def hallmark_cooccurrences(terms, hallmark_filter=None):
    data = OrderedDict()
    # Initialize all hallmark counts to zero. This is required because
    # the API omits keys with zero occurrences from its dict.
    for term in terms:
        data[term] = OrderedDict()
        for code, hm in hallmark_codes.items():
            data[term][hm] = 0
    # Get totals for hallmarks, store as (None, hm)
    data[None] = {}
    hallmark_total = db_controller.getHallmarksCount()
    for code, count in sorted(hallmark_total.items()):
        data[None][hallmark_codes[code]] = count
    # Get hallmark-term cooccurrences and term totals
    for term in terms:
        term_total, hallmark_count = db_controller.getHallmarksForQuery(term)
        data[term][None] = term_total
        for code, count in hallmark_count.items():
            hm = hallmark_codes[code]
            data[term][hm] = count
    total = db_controller.getTotalNumberOfSentences()
    data[None][None] = total
    if hallmark_filter is not None:
        data = filter_cooccurrence_data(data, hallmark_filter.values())
    debug('cooccurrence data: {}'.format(data))
    return CountStats(data)

def fill_template_arguments(args):
    """Add global arguments to template to given dictionary."""
    args.update({
        'measure': getarg('measure', DEFAULT_MEASURE),
        'measures': CountStats().measures.keys(),
        'chart_type': getarg('chart_type', DEFAULT_CHART),
        'chart_types': chart_types.keys(),
        'hallmarks': getarg('hallmarks', 'top'),
        'hallmark_options': ['top', 'full'],
        'hallmark_codes': hallmark_codes,
    })
    return args

def render_template_with_globals(template, args):
    """Fill in global arguments and render given template."""
    args = fill_template_arguments(args)
    debug('Rendering {} with args: {}'.format(template, args))
    return render_template(template, **args)


def generate_comparison(terms, measure='npmi'):
    # TODO eliminate duplication with generate_charts
    chart_type='column'
    hallmarks = getarg('hallmarks', 'top')
    hallmark_filter = top_hallmark_codes if hallmarks == 'top' else None

    stats = hallmark_cooccurrences(terms, hallmark_filter)
    m = select_measure(stats, measure)
    measure_name = selected_measure(stats, measure)

    assert(len([t for t in stats if t is not None]) == 2)

    # Get raw counts, excluding standalone
    term_counts = { k: v for k, v in stats.getcounts().items()
                    if k is not None }

    ssmetrics = term_significance(term_counts)
    def format_pvalue(term):
        p = '{:.2f}'.format(ssmetrics['pvalue'].get(term))
        if p == '0.00':
            p = '< 0.01'
        return ' (p {})'.format(p)

    charts = []
    render_large = True

    for i, term in enumerate(terms):
        position = POS_LEFT if i%2 == 0 else POS_RIGHT
        term_total = int(stats.count(term, None))
        values = [ (hm, m(term, hm)) for hm in stats[term] if hm is not None ]
        # Mark statistical significance in labels
        values = [
            (hm + format_pvalue(hm), v)
            for hm, v in values
        ]
        label = '{} ({})'.format(term, term_total)
        Chart = select_chart(chart_type)
        charts.append(Chart(
            label, values, term, measure=measure_name, position=position,
            render_large=render_large, hallmarks=hallmarks
        ))

    template_args = {
        'includereset': True,
        'hiddenparams': hidden_parameters(terms),    # Previous queries
        'containers': Markup('\n'.join(c.container() for c in charts)),
        'chartdata': Markup('\n'.join(c.datastr() for c in charts)),
        'chartinit': Markup('\n'.join(c.initstr() for c in charts)),
        'DEBUG' : DEBUG,
    }
    return render_template_with_globals('comparison.html', template_args)


def generate_charts(terms, measure='npmi', chart_type='polar'):
    hallmarks = getarg('hallmarks', 'top')
    hallmark_filter = top_hallmark_codes if hallmarks == 'top' else None

    stats = hallmark_cooccurrences(terms, hallmark_filter)
    m = select_measure(stats, measure)
    measure_name = selected_measure(stats, measure)

    charts = []
    render_large = True

    for term in terms:
        term_total = int(stats.count(term, None))
        values = [ (hm, m(term, hm)) for hm in stats[term] if hm is not None ]
        label = '{} ({})'.format(term, term_total)
        Chart = select_chart(chart_type)
        charts.append(Chart(
            label, values, term, measure=measure_name,
            render_large=render_large, hallmarks=hallmarks
        ))

    fixed_legend = get_legend(hallmarks)
    if fixed_legend is not None:
        fixed_legend = Markup(fixed_legend)

    template_args = {
        'includereset': True,
        'hiddenparams': hidden_parameters(terms),    # Previous queries
        'containers': Markup('\n'.join(c.container() for c in charts)),
        'chartdata': Markup('\n'.join(c.datastr() for c in charts)),
        'chartinit': Markup('\n'.join(c.initstr() for c in charts)),
        'fixedlegend': fixed_legend,
        # Legends will be identical, use that of the first chart. Note
        # that the generated legend is only used as a fallback in case
        # there is no preformatted legend (i.e. fixed_legend is None).
        'legend': Markup(charts[0].legendstr()),
        'DEBUG' : DEBUG,
    }
    return render_template_with_globals('chart.html', template_args)
