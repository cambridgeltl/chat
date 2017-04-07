from collections import OrderedDict

from logging import debug

from common import pretty_dumps

from hallmarks import top_hallmark_codes, hallmark_codes
from hallmarks import top_hallmark_colors, full_hallmark_colors


# Chart horizontal position values
POS_ONLY, POS_LEFT, POS_RIGHT = range(3)


class Chart(object):
    next_index = 1

    base_colors = [
        '#318f5a',
        '#52ab24',
        '#7fbf00',
        '#ccc800',
        '#e1b900',
        '#e7a400',
        '#e78b00',
        '#ea6f16',
        '#ed5858',
        '#d64891',
        '#a84ba2',
        '#755ea5',
        '#40758b',
    ]
    
    def __init__(self, title, data, query=None, clip_range=None,
                 measure=None, position=POS_ONLY,
                 render_large=True, hallmarks='top'):
        """Initialize Chart.

        Args:
            title: Title string to display with chart.
            data: List of (label, value) pairs.
            query: The query used to generate the chart. Used for drill-down.
            clip_range: Integer tuple (min, max) giving interval to clip value
               to. Use None, (min, None), (None, max) for no clipping and open
               intervals.
        """
        self.title = title
        self.data = data
        self.query = query
        self.clip_range = clip_range
        self.measure = measure
        self.idx = Chart.next_index
        Chart.next_index += 1
        self.validate_data()
        self.position = position
        self.render_large = render_large
        self.hallmarks = hallmarks

    def validate_data(self):
        if self.clip_range is not None:
            minv, maxv = self.clip_range
            minv = minv if minv is not None else float('-inf')
            maxv = maxv if maxv is not None else float('inf')
            if any(l for l, v in self.data if not minv <= v <= maxv):
                debug('clipping values to ({}, {})'.format(minv, maxv))
            self.data = [(l, (min(max(v, minv), maxv))) for l, v in self.data]

    def color(self, index):
        if self.hallmarks == 'top':
            colors = top_hallmark_colors
        elif self.hallmarks == 'full':
            colors = full_hallmark_colors
        else:
            colors = Chart.base_colors
        return colors[index % len(colors)]

    def highlight(self, index):
        # rough lighten
        base = self.color(index)[1:]
        rgb = tuple(int(base[2*i:2*i+2], 16) for i in range(3))
        lighter = tuple(min(255, i+32) for i in rgb)
        return '#%02x%02x%02x' % lighter

    def container(self):
        """Return string for HTML element containing the chart."""
        if self.position == POS_LEFT:
            chart_class = "chartwrapper-left"
        elif self.position == POS_RIGHT:
            chart_class = "chartwrapper-right"
        else:
            chart_class = "chartwrapper"
        # TODO the link generation here uses too much information
        # about the system internals. Rethink.
        return '''
            <div class="{4}" id="wrapper-{0}">
              <canvas class="chart" id="chart-{0}"></canvas>
                <div class="chartlinks">
                  <a href="/search?q={1}">Show matches for {1}</a> |
                  <a href="/chartdata?q={1}&measure={2}&hallmarks={3}">Get chart data for {1}</a>
                </div>
              </div>
        '''.format(self.idx, self.query, self.measure, self.hallmarks,
                   chart_class)

    def labels(self):
        """Return list of chart labels."""
        return [d[0] for d in self.data]

    def values(self):
        """Return list of chart data values."""
        return [d[1] for d in self.data]

    def colors(self):
        """Return list of chart background colors."""
        return [self.color(i) for i in range(len(self.data))]

    def codes(self):
        """Return list of hallmark codes."""
        if self.hallmarks == 'top':
            return top_hallmark_codes
        elif self.hallmarks == 'full':
            return hallmark_codes
        else:
            raise ValueError('codes only defined for hallmark charts')

    def highlights(self):
        """Return list of chart background highlight colors."""
        return [self.highlight(i) for i in range(len(self.data))]

    def options(self):
        """Return dictionary of chart options."""
        return {
            #'responsive': False,    # don't resize w/canvas container
            'responsive': True,    # resize w/canvas container
            'maintainAspectRatio': False,    # resize w/canvas container
            'legend': {
                'display': False
            },
            'title': {
                'display': True,
                'text': self.title,
            },
            'height': '500'
        }

    def datastr(self, comparison = False):
        if not self.position == POS_LEFT:
            labels = self.labels()
        else:
            labels = ['' for k in self.labels()]
        return 'var chartData{} = '.format(self.idx) + pretty_dumps({
            'labels': labels,
            'datasets': [
                {
                    'data': self.values(),
                    'backgroundColor': self.colors(),
                    'hoverBackgroundColor': self.highlights(),
                    'codes': self.codes().keys(),
                    'query': self.query
                },
            ],
        }, float_precision=3)

    def contextstr(self):
        context_alter = ''
        if self.render_large:
            context_alter = '''
                ctx{0}.canvas.height = 400;
            '''.format(self.idx)
        return context_alter

    def legendstr(self):
        """Return string for chart data in JS."""
        return '''
            var legend{0} = document.getElementById("chart-legend");
            var legendstr{0} = chart{0}.generateLegend();
            legendstr{0} = legendstr{0}.replace(/(<span.*?>)(.*?)(<\/span>)/g, '$1$3$2');
	    legend{0}.innerHTML = legendstr{0};
        '''.format(self.idx)

    def scalestr(self):
        """Return string for fixing step bug in chartjs."""
        reverse_configuration = ''
        if self.position == POS_LEFT:    # reversed
            reverse_configuration = '''
                    xAxes: [{
                        ticks: {
                          reverse: true,
                        }
                    }],
                    yAxes: [{
                        ticks: {
                            fontSize: 10
                        }
                    }],
            '''
        return '''
            options.scales = {{
                {0}
                ticks: {{
                    callback: function (value, index, values) {{
                        if(value % 1 != 0) {{
                            value = parseFloat(value).toFixed(2);
                        }}
                        return value * -1;
                    }}
                }},
            }};
        '''.format(reverse_configuration)

    def default_initstr(self, chart_type):
        return '''
            var options = {2};
            {3}
            var ctx{0} = document.getElementById("chart-{0}").getContext("2d");
            {4}
            window.chart{0} = new Chart(ctx{0}, {{
                type: "{1}",
                data: chartData{0},
                options: options
            }});
        '''.format(self.idx, chart_type, pretty_dumps(self.options()), self.scalestr(), self.contextstr())

    def initstr(self):
        """Return string for initializing chart in JS."""
        raise NotImplementedError()


class PolarChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(PolarChart, self).__init__(title, data, query,
                                         clip_range=(0, None), **kwargs)

    def initstr(self):
        return self.default_initstr('polarArea')


class RadarChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(RadarChart, self).__init__(title, data, query,
                                         clip_range=(0, None), **kwargs)

    def initstr(self):
        return self.default_initstr('radar')


class BarChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(BarChart, self).__init__(title, data, query, **kwargs)

    def initstr(self):
        return self.default_initstr('bar')

class ColumnChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(ColumnChart, self).__init__(title, data, query,
                                          clip_range=(0, None), **kwargs)

    def initstr(self):
        return self.default_initstr('horizontalBar')

class PieChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(PieChart, self).__init__(title, data, query,
                                       clip_range=(0, None), **kwargs)

    def initstr(self):
        return self.default_initstr('pie')

class DoughnutChart(Chart):
    def __init__(self, title, data, query=None, **kwargs):
        super(DoughnutChart, self).__init__(title, data, query,
                                            clip_range=(0, None), **kwargs)

    def initstr(self):
        return self.default_initstr('doughnut')

chart_types = OrderedDict([
    ('polar', PolarChart),
    ('radar', RadarChart),
    ('bar', BarChart),
    ('column', ColumnChart),
    ('pie', PieChart),
    ('doughnut', DoughnutChart),
])
default_chart = PolarChart
