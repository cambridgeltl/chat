const { Provider, connect } = window.ReactRedux
const { createStore, combineReducers } = window.Redux;

//utility functions

function LightenDarkenColor(col, amt) {
      
        var usePound = false;
      
        if (col[0] == "#") {
                    col = col.slice(1);
                    usePound = true;
                }
     
        var num = parseInt(col,16);
     
        var r = (num >> 16) + amt;
     
        if (r > 255) r = 255;
        else if  (r < 0) r = 0;
     
        var b = ((num >> 8) & 0x00FF) + amt;
     
        if (b > 255) b = 255;
        else if  (b < 0) b = 0;
     
        var g = (num & 0x0000FF) + amt;
     
        if (g > 255) g = 255;
        else if (g < 0) g = 0;
     
        return (usePound?"#":"") + (g | (b << 8) | (r << 16)).toString(16);
      
}



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


function addDocToClipboard(pmid,title) {
    return {
        type: "ADD_TO_CBOARD",
        payload: {pmid, title}	
    }
}

function removeDocFromClipboard(pmid) {
    return {
        type: "DEL_FROM_CBOARD",
        payload: {pmid}	
    }
}

function clearDocClipboard() {
    return {
        type: "CLEAR_CBOARD",
        payload: {}	
    }
}





/* reducers */

function dataR(state={ active_dataset:{}, datasets:{}, metadata:{}, docclipboard: []  }, action) {

    var copyState = JSON.parse(JSON.stringify( state ))
    switch (action.type) {
        case "CLEAR_CBOARD": {
            copyState.docclipboard = []
	    return copyState
        }
        case "ADD_TO_CBOARD": {
            copyState.docclipboard =
		     _.concat(
		     _.filter(copyState.docclipboard, (o) => action.payload.pmid != o.pmid ) ,
		    (_.filter(copyState.docclipboard, (o) => action.payload.pmid == o.pmid ).length == 0 ? 
			[action.payload] : []) 
		    )
            return copyState
        }
        case "DEL_FROM_CBOARD": {

	    console.log("DEL_FROM_CBOARD")
	    console.log(_.filter(copyState.docclipboard, (o) => action.payload.pmid != o.pmid ) )

            copyState.docclipboard =
                    _.filter(copyState.docclipboard, (o) => action.payload.pmid != o.pmid )
	    return copyState
	}
        case "SET_METADATA": {
            return _.merge({},copyState, action.payload)
        }
        case "SET_ACTIVEDATA": {
            copyState.active_dataset =  _.merge({},copyState.active_dataset, action.payload)
	    return copyState
        }
        case "ADD_DATA": {
            delete copyState.datasets[_.keys(action.payload.id)[0]]
	    copyState.datasets = _.merge({},copyState.datasets,action.payload) 
            return copyState
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
            delete copyState.datasets[action.payload.id]
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
    this.plotGraph = this.plotGraph.bind(this);
    this.renderLegend = this.renderLegend.bind(this);
  }

  componentDidMount() {
    this.plotGraph()
  }


  componentDidUpdate(prevProps, prevState) {
    if (!_.isEqual(prevProps, this.props)){
        this.plotGraph()
    }
  }

  plotGraph() {

      $('#chart1div').empty()
      $('#chart1div').html('<canvas class="chart" id="chart-1" ></canvas>')

      var hallmark_codes =
          this.props.metadata[this.props.hallmarks+"_hallmark_codes"]
      var hallmark_codes_arr = _.sortBy( _.keys(hallmark_codes) )
      var hallmark_names_arr = _.map(hallmark_codes_arr, (o) => hallmark_codes[o])
      var data = _.map(hallmark_names_arr, (o) => this.props.data[o])

      console.log(this.props.hallmarks+"_hallmark_codes")
      console.log(this.props.metadata)
      console.log(hallmark_codes)

      var chartData1 = {
	  "datasets": [
	      {
		  "backgroundColor": this.props.metadata[this.props.hallmarks+"_hallmark_colors"] ,
		  "codes": hallmark_codes_arr,
		  "data": data,
                  "hoverBackgroundColor": 
                  _.map(this.props.metadata[this.props.hallmarks+"_hallmark_colors"],(o)=>LightenDarkenColor(o,20)),
		  "query": this.props.term
	      }
	  ],
	  "labels": hallmark_names_arr
      }

      console.log(chartData1)

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


  renderLegend() {
      var colors = this.props.metadata[this.props.hallmarks+"_hallmark_colors"] 
      var hallmark_codes = this.props.metadata[this.props.hallmarks+"_hallmark_codes"]
      var hallmark_codes_arr = _.sortBy( _.keys(hallmark_codes) )
      var hallmark_names_arr = _.map(hallmark_codes_arr, (o) => hallmark_codes[o])
      var data = _.map(hallmark_names_arr, (o) => this.props.data[o])

      console.log(this.props.hallmarks)
      console.log(this.props.metadata[this.props.hallmarks+"_hallmark_codes"])
      console.log(_.range(0, hallmark_codes.length))

      return (
        <div style={{marginTop: '30px'}}>
            <table style={{borderSpacing: '10px', borderCollapse: 'separate'}}>
                <tbody>
                {_.map(_.range(0, hallmark_codes_arr.length), 
                    (i) => (
                        <tr key={i}>
                            <td style={{backgroundColor:colors[i], margin:'3px'}}>
                                &nbsp;&nbsp;&nbsp;
                            </td>
                            <td>{hallmark_names_arr[i]}</td>
                            <td>{data[i].toFixed(4)}</td>
                        </tr>
                        )
                    )
                }
                </tbody>
            </table>
        </div>
      )

  }


  render() {
      return (
        <div>
            <div id={'chart1div'}  style={{textAlign: 'center'}}>
               
            </div>
            <div>
                {this.renderLegend()}
            </div>
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
    
    this.handleClick = this.handleClick.bind(this);
  }


  handleClick(e,pmid,title,remove) {
    console.log('remove is ')
    console.log(remove)
    e.preventDefault();
    if (remove){
	this.props.removefromcboard_(pmid)
    }	    
    else {
	this.props.addtocboard_(pmid,title)
    }
  }
	
  render() {

    var item = this.props.item
    var notadded = _.filter(this.props.docclipboard, (o) => item.pmid == o.pmid ).length == 0

    return (
      <div style={{marginBottom: '30px'}}>
        <h4>
	    {this.props.showAddRem ? <a href="#" onClick={(e) =>  this.handleClick(e,item.pmid,item.title,!notadded)} >
		{ notadded ? 
			<i className="fas fa-plus-square"></i> :
			<i className="far fa-minus-square"></i> }
	    </a> : null }
	    <a href={"/pubmed/"+item.pmid}>{' ' + item.title + ' '}</a>
	    <a target="_blank" href={"https://www.ncbi.nlm.nih.gov/pubmed/"+item.pmid}>
		<i className="fas fa-external-link-square-alt"></i>
	    </a> 
	</h4>
	
	{item.hasOwnProperty('epubdate') && item.hasOwnProperty('fulljournalname') ?
	<div>({item.pubdate.substring(0,4)}) - {item.fulljournalname} </div> : null }
	
	<em>{item.text}</em>
      </div>
    );
  }
}
const ReduxedSearchItem = connect(
    (state) => {return { metadata: state.dataR.metadata, activedata:state.dataR.active_dataset, 
			 docclipboard: state.dataR.docclipboard }; },
    (dispatch) => {return {
	    addtocboard_ : (pmid,title) => { dispatch(addDocToClipboard(pmid,title)) },
	    removefromcboard_  : (pmid)  => {  dispatch(removeDocFromClipboard(pmid)) },
       	          };    
    }
)(SearchItem)




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
    this.fillParams = this.fillParams.bind(this);
    this.runQuery = this.runQuery.bind(this);
  }

  fillParams(data) {
    var params = _.pick(data,['term','hm','hallmarks','measure','offset'])
    if (data.hasOwnProperty('pmids')) { 
      params['pmids']=data.pmids.join(','); 
      delete params['term']
    }
    if (params.hasOwnProperty('term')){
      params['q'] = params['term']
      delete params['term']
    }
    params['asjson'] = 1
    return params
  }

  runQuery(props) {

	var setactivedata_ = props.setactivedata_
	var setpmcdataid_ = props.setpmcdataid_
	var addData_ = props.addData_

	var dataset = props.dataset
	var params = dataset == null ? this.fillParams(this.state.formVals) : this.fillParams(props.datasets[dataset])
		    // { q:formVals.term, measure:formVals.measure, hallmarks: formVals.hallmarks, asjson: 1   }

	var setDataRespFn = dataset == null ? setactivedata_ : (d) => addData_(dataset,d)
	
	$.get( "/search", params , function( data ) { 
	    //setactivedata_(data)
	    setDataRespFn(data)

	    if (!data.hasOwnProperty('results') || data.results.length == 0){return }

	    var pmids = _.map(data.results, (o) => o.pmid).join(',')	
	    $.getJSON("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="+pmids+"&retmode=json&tool=crab2&email=tss42@cam.ac.uk", function(data){setpmcdataid_(dataset, data.result)}); 
	}, "json");
	
	$.get( "/chartdata", params, function( data ) { 
	    setDataRespFn(data[0])  //setactivedata_(data[0])
	}, "json");

  }

  componentDidUpdate(prevProps, prevState) {
    if (this.props.dataset != prevProps.dataset){
	var dataset = this.props.dataset
	var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
	if (!data.results && dataset != null){
	    this.runQuery(this.props)
	}
    }
  }

  componentDidMount() {
    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
    if (!data.results && dataset != null){
	this.runQuery(this.props)
    }
  }
	
  handleClick(e) {
    e.preventDefault();
    var formVals = this.state.formVals
    if (formVals.term.length > 0 ) {
	this.props.clearcboard_()
	this.runQuery(this.props)

	/*
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
	*/

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

    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 

    if (_.isEmpty(data) && dataset == null){
	return (
	    <div className="row">
		<div className="col-md-8 offset-md-2">
		    <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
				      formVals={this.state.formVals}/>
		</div>
	    </div>
	);
    }

    if (dataset != null && !data.results ) {
	return (
	    <div className="row">
		<div className="col">
		    <div style={{textAlign: 'center'}}> <img src="/static/img/loading.svg" /> </div>
		</div>
	    </div>
	)
    }


    return (
	<div className="row">
	    <div className="col-md-7 order-md-2">
                <div style={{marginTop: '30px', marginBottom: '30px'}}>
                    
		    { dataset == null ?  <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
                        formVals={this.state.formVals}/> : null }
                    <div className="d-none d-md-block" style={{marginTop: '30px'}}>
                        {data.results ? 
			 _.map(data.results,function(o,ind){ 
			    return (<ReduxedSearchItem showAddRem={dataset == null} item={o}  key={ind} />) }):
			 null}
                    </div>
		</div>
	    </div>
	    <div className="col-md-5 order-md-1">
		<div style={{marginTop: '30px', marginBottom: '30px'}}>
		    {data.values ? 
			<ReduxedMyChart data={data.values} term={data.term}
				      hallmarks={data.hallmarks} /> : null }
		</div>
	    </div>
	    <div className="d-md-none">
                <div style={{marginTop: '30px', marginBottom: '30px'}}>
                    <div>
                        { data.results ? _.map(data.results,function(o,ind){ 
			    return (<ReduxedSearchItem showAddRem={dataset == null} item={o}  key={ind} />) }):null}
                    </div>
		</div>
	    </div>
	</div>
    );

  }
}
const ReduxedQueryPanel = connect(
    (state) => {return { metadata: state.dataR.metadata, 
			 activedata:state.dataR.active_dataset, 
			 datasets: state.dataR.datasets }; },
    (dispatch) => {return {
	    setactivedata_ : (activedata) => { dispatch(setActiveData(activedata)) },
	    setpmcdataid_  : (id, pmcresults)  => {  dispatch(setPMCData(id,pmcresults)) }, 
	    addData_  : (id,data)  => {  dispatch(addData(id,data)) },
	    clearcboard_  : ()  => {  dispatch(clearDocClipboard()) },
       	          };    
    }
)(QueryPanel)


class Chat extends React.Component {
  constructor(props) {
    super(props);
    this.renderSaveModal = this.renderSaveModal.bind(this);
    this.handleSaveClick = this.handleSaveClick.bind(this);
    this.handleSaveChange = this.handleSaveChange.bind(this);
    this.generateNewDatasetId = this.generateNewDatasetId.bind(this);
    this.handleActivePanelClick = this.handleActivePanelClick.bind(this);
    this.state = {activepanel: null , 
		  queryDatasetName: this.generateNewDatasetId('Qry-'), 
		  docsDatasetName: this.generateNewDatasetId('Doc-') }
  }

  generateNewDatasetId(prefix) {
    var code = null
    while (code == null ||  _.indexOf( _.keys(this.props.datasets), code ) != -1  ) {
	code = prefix + Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 4)
    } 
    return code
  }

  componentDidMount() {
    var setmetadata_ = this.props.setmetadata_
    if (!this.props.metadata.hasOwnProperty('measure')){
	$.get( "/metadata", function( data ) {
	  setmetadata_(data)
	}, "json");
    }
  }

  handleSaveChange(e,key) {    
    this.setState({key: e.target.value })
  }

  handleSaveClick(e,type) {
    e.preventDefault();

    //add to the datasets
    if (type == 'query' && this.props.activedata.hasOwnProperty('term')  && 
	this.props.activedata.hasOwnProperty('results') && this.props.activedata.hasOwnProperty('values') ) { 
	this.props.addData_(this.state.queryDatasetName,_.pick(this.props.activedata,['term','hm','hallmarks','measure','offset']))
	this.setState({queryDatasetName: this.generateNewDatasetId('Qry-') })
    }
    else if (type == 'docs' && this.props.docclipboard.length > 0  ) {
	this.props.addData_(this.state.docsDatasetName,
	_.merge({}, _.pick(this.props.activedata,['measure', 'hallmarks']), 
		{'pmids':_.map(this.props.docclipboard, (o) => o.pmid )}))
	this.setState({docsDatasetName: this.generateNewDatasetId('Doc-') })
	this.props.clearcboard_()
    }
    $('.modal').modal('hide');
  }

  handleActivePanelClick(e,activepanel){
    if (e) {e.preventDefault();}
    this.setState({activepanel})
  }


  renderSaveModal(type) {
    var that = this
 
    return (
	<div className="modal" tabIndex="-1" role="dialog" id={'savemodal'+type}  >
	  <div className="modal-dialog" role="document" >
	    <div className="modal-content">
	      <div className="modal-header">
		<h5 className="modal-title">{type == 'query' ? 'Save Current Query' : 'Save Selected Docs'  }</h5>
		<button type="button" className="close" data-dismiss="modal" aria-label="Close">
		  <span aria-hidden="true">&times;</span>
		</button>
	      </div>
	      <div className="modal-body">
		{type == 'docs' ?
		_.map(this.props.docclipboard, (o) => 
		    <div style={{margin: '10px'}} key={o.pmid}>
			<h6>
			    <a href="#" onClick={(e) => { e.preventDefault();that.props.removefromcboard_(o.pmid); } } >
				<i className="far fa-minus-square"></i>
			    </a>
			    {' ' + o.title}
			</h6>
		    </div> )
		: <p>No documents selected to save</p> }
	      </div>
	      <div className="modal-footer">
		<input name="datasetname" 
		       value={type == 'query' ? this.state.queryDatasetName : this.state.docsDatasetName} 
		       onChange={(e) => this.handleSaveChange(e,type == 'query' ? 
				this.state.queryDatasetName : this.state.docsDatasetName )} />
		<button type="button" className="btn btn-primary" onClick={(e) => this.handleSaveClick(e,type)}>
		    Save
		</button>
		<button type="button" className="btn btn-secondary" data-dismiss="modal">Cancel</button>
	      </div>
	    </div>
	  </div>
	</div>
    )

  }
	
  render() {
    var activedata = this.props.activedata
    
    var save_query_enabled = this.props.activedata.hasOwnProperty('term')  && 
			     this.props.activedata.hasOwnProperty('results') && this.props.activedata.hasOwnProperty('values') 


    return (
	<div className="container" style={{marginTop:'40px'}}>
	    <div className="row">
		<div className="col-md-8 offset-md-2" style={{textAlign: 'center'}}>
		    <img src="/static/img/chat.png" height="100" />
		    <h4>Cancer Hallmarks Analytics Tool</h4>
		</div>
	    </div>

	{!this.props.metadata.hasOwnProperty('measure') ?
            <div style={{textAlign: 'center'}}> <img src="/static/img/loading.svg" /> </div>	: 

	    <div>
		{!_.isEmpty(activedata) ?
		<div className="row" style={{marginTop: '30px'}}>
		    <div className="col">
			<div style={{display: 'flex', flexDirection: 'row' , 
				     justifyContent: this.state.activepanel == null ?  'space-between' : 'flex-start' }}>
			    <ul className="list-inline">
				<li className="list-inline-item">
				    <button onClick={(e) => this.handleActivePanelClick(e,null)} 
					type="button" 
					className={"btn btn-"+(this.state.activepanel == null ? "" : "outline-" )+"primary"}>
					    Active
				    </button>
				</li>
				{_.map(Object.keys(this.props.datasets), (o) => 
				 (<li className="list-inline-item" key={o}>
				    <button onClick={(e) => this.handleActivePanelClick(e,o)} 
					type="button" 
					className={"btn btn-"+(this.state.activepanel == o ? "" : "outline-" )+"secondary"}>
					{o}
				    </button>
				  </li>)) }
			    </ul>
			    {this.state.activepanel == null ?
			    <ul className="list-inline">
				<li className="list-inline-item">
				    <button type="button" className={"btn btn-outline-primary"} 
					    data-toggle="modal" data-target="#savemodalquery"
					    disabled={!save_query_enabled}
					    >
					<i className="far fa-save"></i> Query
				    </button>
				</li>
				<li className="list-inline-item">
				    <button type="button" 
					    className={"btn btn-outline-primary"}
					    disabled={this.props.docclipboard.length == 0}	
					    data-toggle="modal" data-target="#savemodaldocs" >
					<i className="far fa-save"></i> Docs ({this.props.docclipboard.length}) 
				    </button>
				</li>
			    </ul> : null }
			</div>
		    </div>
		</div> : null }
		<ReduxedQueryPanel dataset={this.state.activepanel} />
		{this.renderSaveModal('query')}
		{this.renderSaveModal('docs')}
	    </div>
       	}
	</div>
    );
  }
}
const ReduxedChat = connect(
    (state) => {return { metadata: state.dataR.metadata , 
			 activedata:state.dataR.active_dataset, datasets: state.dataR.datasets,
			 docclipboard: state.dataR.docclipboard }; },
    (dispatch) => {return { 
        setmetadata_ : (metadata) => { dispatch(setMetadata(metadata)) }, 
	removefromcboard_  : (pmid)  => {  dispatch(removeDocFromClipboard(pmid)) },
	addData_  : (id,data)  => {  dispatch(addData(id,data)) },
	clearcboard_  : ()  => {  dispatch(clearDocClipboard()) },
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
