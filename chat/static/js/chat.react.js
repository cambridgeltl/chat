const { Provider, connect } = window.ReactRedux
const { createStore, combineReducers } = window.Redux;


//reducer for queries

/* user functions */

function setMetadata(metadata) {

    return {
        type: "SET_METADATA",
        payload: { metadata }
    }

}

function addData(id,data) {
    var payload = []
    payload[id] = data
    return {
        type: "ADD_DATA",
        payload
    }
}


function removeData(id) {
    return {
        type: "REMOVE_DATA_BYID",
        payload: {id}
    }
}


function setActiveData(active_dataset) {
    return {
        type: "SET_ACTIVEDATA",
        payload: active_dataset
    }
}

function setPMCData(id,pmcresults) {
    return {
        type: "SET_PMCDATA",
        payload: {pmcresults, id}	
    }
    
}

/* reducers */

function dataR(state={ active_dataset:{}, datasets:{}, metadata:{}  }, action) {

    var copyState = JSON.parse(JSON.stringify( state ))
    switch (action.type) {
        case "SET_METADATA": {
            return _.merge({},copyState, action.payload)
        }
        case "SET_ACTIVEDATA": {
            copyState.active_dataset =  _.merge({},copyState.active_dataset, action.payload)
	    return copyState
        }
        case "ADD_DATA": {
            return _.merge({},copyState, action.payload)
        }
        
	case "SET_PMCDATA": {
	    var dataset = action.payload.id === null ? 
			  copyState.active_dataset : 
			  copyState.datasets.hasOwnProperty(action.payload.id) ?
			  copyState.datasets[action.payload.id] : null 
			   
	    if (dataset != null && dataset.hasOwnProperty('results') &&
		dataset.results.length > 0) {
		dataset.results = _.map(dataset.results, 
				  function(o,ind) { 
				    if (!action.payload.pmcresults.hasOwnProperty(o.pmid)) {return o}
				    return _.merge({},action.payload.pmcresults[o.pmid],o)
				  })
		if (action.payload.id === null){
		    copyState.active_dataset = dataset
	        } else {
		    copyState.datasets[action.payload.id] = dataset
		}	
	    }
            return copyState
        }
        
	case "REMOVE_DATA_BYID": {
            delete thisIsObject[action.payload.id]
	    return copyState
        }
    }
    return state
}




class SearchBox extends React.Component {
  constructor(props) {
    super(props);
  }
	
  render() {

    var metadata = this.props.metadata
    var formVals = this.props.formVals
    var handleChange = this.props.handleChange

    console.log(formVals)

    return (
	<div>
	    <form>
	      <div className="form-row">
		<div className="form-group col-12">
    		    <div className="input-group">
    			<input type="text" className="form-control" id="inputQuery" 
			       placeholder="Enter query" value={formVals.term} onChange={(e)=>handleChange('term',e)} />
			<div className="input-group-append">
			    <button type="submit" className="btn btn-primary" onClick={this.props.handleClick}>Go!</button>
			</div>
		    </div>		    
		</div>
	      </div>
	      <div className="form-row">
		<div className="form-group col-6">
		  <label htmlFor="inputState">Metric</label>
		  <select id="inputState" className="form-control" value={formVals.measure} 
			  onChange={(e)=>handleChange('measure',e)}
		  >
		    { _.map(metadata.measures,function(o,ind){ return (<option  key={ind}>{o}</option>) })}
		  </select>
		</div>
		<div className="form-group col-6">
		  <label htmlFor="inputState">Hallmarks</label>
		  <select id="inputState" className="form-control" value={formVals.hallmarks}
			  onChange={(e)=>handleChange('hallmarks',e)}
		  >
		    { _.map(metadata.hallmark_options,function(o,ind){ return (<option  key={ind}>{o}</option>) })}
		  </select>
		</div>
	      </div>
	    </form>
	</div>
    );


    /*
	<div className="form-group col-4">
	  <label htmlFor="inputState">Chart</label>
	  <select id="inputState" className="form-control" value={formVals.chart_type}
		  onChange={(e)=>handleChange('chart_type',e)}
	  >
	    { _.map(metadata.chart_types,function(o,ind){ return (<option  key={ind}>{o}</option>) })}
	  </select>
	</div>
    */


  }
}
const ReduxedSearchBox = connect(
    (state) => {return { metadata: state.dataR.metadata }; },
    (dispatch) => {return { 
    };    
    }
)(SearchBox)





class MyChart extends React.Component {
  constructor(props) {
    super(props);
    this.state = {isToggleOn: true};

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  componentDidMount() {

      var chartData1 = {
	  "datasets": [
	      {
		  "backgroundColor": this.props.metadata[this.props.hallmarks+"_hallmark_colors"] ,
		  "codes": [
		      "1",
		      "2",
		      "3",
		      "4",
		      "5",
		      "6",
		      "7",
		      "8",
		      "9",
		      "x"
		  ],
		  "data": [
		      0.106,
		      0,
		      0.026,
		      0.321,
		      0.309,
		      0.353,
		      0.111,
		      0.354,
		      0.229,
		      0.056
		  ],
		  "hoverBackgroundColor": this.props.metadata[this.props.hallmarks+"_hallmark_colors"] ,
		  "query": this.props.term
	      }
	  ],
	  "labels": [
	      "INVASION AND METASTASIS",
	      "IMMUNE DESTRUCTION",
	      "CELLULAR ENERGETICS",
	      "REPLICATIVE IMMORTALITY",
	      "EVADING GROWTH SUPPRESSORS",
	      "GENOME INSTABILITY AND MUTATION",
	      "INDUCING ANGIOGENESIS",
	      "RESISTING CELL DEATH",
	      "SUSTAINING PROLIFERATIVE SIGNALING",
	      "TUMOR PROMOTING INFLAMMATION"
	  ]
      }


      var options = {
	  "height": "500",
	  "legend": {
	      "display": false
	  },
	  "maintainAspectRatio": true,
	  "responsive": true,
	  "title": {
	      "display": true,
	      "text": this.props.term
	  }
      };

      options.scales = {
	  ticks: {
	      callback: function (value, index, values) {
		  if(value % 1 != 0) {
		      value = parseFloat(value).toFixed(2);
		  }
		  return value * -1;
	      }
	  },
      };
      var ctx1 = document.getElementById("chart-1").getContext("2d");
      ctx1.canvas.height = 300;
      options.hover = {
	  onHover: function(e) {
	      var cnv = document.getElementById("chart-1");
	      cnv.style.cursor = e[0] ? "pointer" : "default";
	  }
      };
      window.chart1 = new Chart(ctx1, {
	  type: "doughnut",
	  data: chartData1,
	  options: options
      });

      console.log('Chart 1')
      console.log(window.chart1)
      
  }
	
  handleClick() {
    this.setState(prevState => ({
      isToggleOn: !prevState.isToggleOn
    }));
  }

  render() {
    return (
    <div  style={{textAlign: 'center'}}>
       <canvas className="chart" id="chart-1" >
       </canvas>
    </div>
    );
  }
}
const ReduxedMyChart = connect(
    (state) => {return { metadata: state.dataR.metadata }; },
    (dispatch) => {return {}; }
)(MyChart)




class SearchItem extends React.Component {
  constructor(props) {
    super(props);
    
  }
	
  render() {

    var item = this.props.item


    return (
      <div style={{marginBottom: '30px'}}>
        <h4><a href={"/pubmed/"+item.pmid}>{item.title}</a> - <a target="_blank" href={"https://www.ncbi.nlm.nih.gov/pubmed/"+item.pmid}>PMD</a></h4>
	
	{item.hasOwnProperty('epubdate') && item.hasOwnProperty('fulljournalname') ?
	<div>({item.pubdate.substring(0,4)}) - {item.fulljournalname} </div> : null }
	
	<em>{item.text}</em>
      </div>
    );
  }
}



class QueryPanel extends React.Component {
  constructor(props) {
    super(props);
    var metadata = this.props.metadata
    

    this.state = { 
		  formVals: {
		  measure: metadata.measure  , 
		  chart_type: metadata.chart_type, 
		  hallmarks:metadata.hallmarks, 
		  term: ""
		  }
	       	};

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }
	
  handleClick(e) {
    e.preventDefault();
    var formVals = this.state.formVals
    if (formVals.term.length > 0 ) {
	var setactivedata_ = this.props.setactivedata_
	var setpmcdataid_ = this.props.setpmcdataid_
	var params = { q:formVals.term, measure:formVals.measure, hallmarks: formVals.hallmarks, asjson: 1   }
	$.get( "/search", params , function( data ) { 
	
	    setactivedata_(data)
	    if (!data.hasOwnProperty('results') || data.results.length == 0){return }

	    var pmids = _.map(data.results, (o) => o.pmid).join(',')	

	    $.getJSON("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="+pmids+"&retmode=json&tool=crab2&email=tss42@cam.ac.uk", 
	    function(data){
		//hello
		setpmcdataid_(null, data.result)	
	    }); 


	}, "json");
	$.get( "/chartdata", params, function( data ) { setactivedata_(data[0])}, "json");
    }
  }

  handleChange(key,e) {
    var toMerge = {}
    toMerge[key] = e.target.value

    this.setState(prevState => (  _.merge({},prevState,{ formVals:toMerge} )  ));
  }



  handleChartClick() {

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
	// TODO: escape special characters in query, grab query and hallmark
	// arguments from config instead of hardcoding "q" and "hm".
	window.location = '/search?q='+query+'&hm='+hallmark_code;
    };


  }



  render() {

    var activedata = this.props.activedata

    if (_.isEmpty(activedata)){
	return (
	    <div className="row">
		<div className="col-md-8 offset-md-2">
		    <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
				      formVals={this.state.formVals}/>
		</div>
	    </div>
	);
    }

    return (
	<div className="row">
	    <div className="col-md-5">
		<div style={{marginTop: '30px', marginBottom: '30px'}}>
		    <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
				  formVals={this.state.formVals}/>
		    {this.props.activedata.values ? 
			<ReduxedMyChart data={this.props.activedata.values} term={this.props.activedata.term}
				      hallmarks={this.state.hallmarks} /> : null }
		</div>
	    </div>
	    <div className="col-md-7">
		<div style={{marginTop: '30px', marginBottom: '30px'}}>
		    { _.map(activedata.results,function(o,ind){ return (<SearchItem item={o}  key={ind} />) })}
		</div>
	    </div>
	</div>
    );

  }
}
const ReduxedQueryPanel = connect(
    (state) => {return { metadata: state.dataR.metadata, activedata:state.dataR.active_dataset }; },
    (dispatch) => {return {
	    setactivedata_ : (activedata) => { dispatch(setActiveData(activedata)) },
	    setpmcdataid_  : (id, pmcresults)  => {  dispatch(setPMCData(id,pmcresults)) }, 
       	          };    
    }
)(QueryPanel)


class Chat extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    var setmetadata_ = this.props.setmetadata_
    if (!this.props.metadata.hasOwnProperty('measure')){
	$.get( "/metadata", function( data ) {
	  setmetadata_(data)
	}, "json");
    }
  }

	
  render() {
    return (
	<div className="container" style={{marginTop:'40px'}}>
	    <div className="row">
		<div className="col-md-8 offset-md-2" style={{textAlign: 'center'}}>
		    <img src="/static/img/chat.png" height="100" />
		    <h4>Cancer Hallmarks Analytics Tool</h4>
		</div>
	    </div>

	{!this.props.metadata.hasOwnProperty('measure') ?
	    <img src="/static/img/loading.svg" />	: <ReduxedQueryPanel /> }
	</div>
    );
  }
}
const ReduxedChat = connect(
    (state) => {return { metadata: state.dataR.metadata }; },
    (dispatch) => {return { 
        setmetadata_ : (metadata) => { dispatch(setMetadata(metadata)) }, 
    };    
    }
)(Chat)


var combinedData = combineReducers({dataR})
var store = createStore(combinedData,
	     window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__() )


if (window.renderReact){
ReactDOM.render(
      <Provider store={store}>
        <ReduxedChat />
      </Provider>
      ,
      document.getElementById('root')
);
}
