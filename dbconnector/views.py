import json

from logging import debug

from flask import request, jsonify

from dbconnector import app, controller

def pretty_dumps(d):
    return json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))

@app.route('/querycount')
def querycount():
    terms = get_query_terms()
    response = {
        'total': controller.getQueryCount(terms[0])
    }
    return jsonify(**response)

@app.route('/hallmarkcount')
def hallmarkcount(expand=False):
    terms = get_query_terms()
    if not terms:
        response = {
            'total': controller.getTotalNumberOfSentences(),
            'hallmarks': controller.getHallmarksCount()
        }
    else:
        values = controller.getHallmarksForQuery(terms[0])
        response = {
            'total': values[0],
            'hallmarks': values[1]
        }
    return jsonify(**response)

@app.route('/search')
def search():
    terms = get_query_terms()
    if not terms:
        return 'Missing query term'
    hallmarks = get_hallmark_terms()
    if hallmarks:
        response = controller.searchTextAndHallmarks(terms[0], hallmarks, 100,
                                                     expandHallmarks=False)
    else:
        response = controller.search(terms[0], 100, expandHallmarks=False)
    return pretty_dumps(response)

def get_query_terms():
    from config import QUERY_PARAMETER as q
    return [ t for t in request.args.getlist(q) if t and not t.isspace() ]

def get_hallmark_terms():
    from config import HALLMARK_PARAMETER as h
    return [ t for t in request.args.getlist(h) if t and not t.isspace() ]
