Chart.defaults.global.onClick = function(event) {
    var chart = this;    // called in context of chart
    var labels = chart.config.data.labels;
    var datasets = chart.config.data.datasets;
    var elements = chart.getElementAtEvent(event);
    var element = elements[0];
    var label = labels[element._index];
    var dataset = datasets[element._datasetIndex];
    // query is a custom attribute of the dataset filled in chart.py
    // to provide access to the user query that generated the chart.
    var query = dataset.query;
    // codes is a custom attribute of the dataset filled in chart.py
    // to map data indices to hallmark codes.
    var hallmark_codes = dataset.codes;
    var hallmark_code = hallmark_codes[element._index];
    // assume that the label of the element clicked on contains the
    // human-readable code of one of the hallmarks and map to code.
    // in comparison mode, statistical significance is marked as part
    // of the label (e.g. "apoptosis (p<0.01)") and must first be
    // removed to get the actual hallmark label.
    var hallmark = label.replace(/ *\(.*\) *$/, '')
{% if DEBUG == true %}
    console.log('click: event   :', event);
    console.log('click: chart   :', chart);
    console.log('click: element :', element);
    console.log('click: dataset :', dataset);
    console.log('click: query   :', query);
    console.log('click: label   :', label);
    console.log('click: codes   :', hallmark_codes);
    console.log('click: hallmark:', hallmark);
    console.log('click: code    :', hallmark_code);
    alert('clicked on '+label+' ('+hallmark_code+') , query: '+query+
	  '\n(set DEBUG = False in config.py to disable this alert)');
{% endif %}
    // TODO: escape special characters in query, grab query and hallmark
    // arguments from config instead of hardcoding "q" and "hm".
    window.location = '/search?q='+query+'&hm='+hallmark_code;
};

 /*
    tab JS following http://callmenick.com/post/simple-responsive-tabs-javascript-css
    TODO move this into a separate .js file
*/
(function() {
    var tabs = function(options) {
	var el = document.querySelector(options.el);
	var navLinks = el.querySelectorAll(options.navLinks);
	var containers = el.querySelectorAll(options.containers);
	var activeIndex = {% if tabindex %}{{ tabindex }}{% else %}0{% endif %};
	var initCalled = false;

	var init = function() {
	    if (!initCalled) {
		el.classList.remove('no-js');
		for (var i = 0; i < navLinks.length; i++) {
		    handleClick(navLinks[i], i);
		}
		initCalled = true;
	    }
	};

	var handleClick = function(link, index) {
	    link.addEventListener('click', function(e) {
		e.preventDefault();
		goToTab(index);
	    });
	};

	var goToTab = function(index) {
	    if (index !== activeIndex && index >= 0 &&
		index <= navLinks.length) {
		navLinks[activeIndex].classList.remove('active');
		navLinks[index].classList.add('active');
		containers[activeIndex].classList.remove('active');
		containers[index].classList.add('active');
		activeIndex = index;
	    }
	};

	return {
	    init: init,
	    goToTab: goToTab
	};
    }
    window.tabs = tabs;
})();

window.onload = function() {
    var queryFormTags = tabs({
	el: '#tabs',
	navLinks: '.tabs-nav-link',
	containers: '.tab'
    });
    queryFormTags.init();
}
