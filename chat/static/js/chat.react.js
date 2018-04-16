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

function addData(id,data,ispaging) {
    return {
        type: "ADD_DATA",
        payload: {data,id, ispaging   }
    }
}


function removeData(id) {
    return {
        type: "REMOVE_DATA_BYID",
        payload: {id}
    }
}


function setActiveData(active_dataset, ispaging) {
    return {
        type: "SET_ACTIVEDATA",
        payload: {data: active_dataset, ispaging} 
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

function setOffset(id,offset) {
    return {
        type: "SET_OFFSET",
        payload: {id, offset}	
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
	    //if is paging, add to exisitng results
            if (action.payload.data.results && action.payload.ispaging){
		var existingresults = copyState.active_dataset.results ? copyState.active_dataset.results : []
		action.payload.data.results = _.concat(existingresults, action.payload.data.results)
	    }
	    //if not paging clear the existing results
	    if (!action.payload.ispaging && action.payload.data.results && copyState.active_dataset.results) {
		delete copyState.active_dataset['results']
	    }
	    copyState.active_dataset =  _.merge({},copyState.active_dataset, action.payload.data)
	    if (action.payload.data.hasOwnProperty('hm')) { 
		copyState.active_dataset.hm = action.payload.data.hm
	    }
	    if (copyState.active_dataset.results){ 
		copyState.active_dataset.offset = copyState.active_dataset.results.length
	    }
	    if (action.payload.data.term === null ){ delete copyState.active_dataset['term'] }
	    if (action.payload.data.pmids === null ){ delete copyState.active_dataset['pmids'] }
	    return copyState
        }
        case "ADD_DATA": {
            //delete copyState.datasets[_.keys(action.payload.data)[0]]
            if (action.payload.data.results && action.payload.ispaging){
		var existingresults = copyState.datasets[action.payload.id].results ? 
			              copyState.datasets[action.payload.id].results : []
		action.payload.data.results = _.concat(existingresults, action.payload.data.results)
	    }

	    copyState.datasets[action.payload.id] = _.merge({},
		copyState.datasets[action.payload.id] ?	copyState.datasets[action.payload.id] : {},
		action.payload.data) 

	    if (action.payload.data.hasOwnProperty('hm')) { 
		copyState.datasets[action.payload.id].hm = action.payload.data.hm
	    }


	    if (copyState.datasets[action.payload.id].results){ 
		
		copyState.datasets[action.payload.id].offset = 
		    copyState.datasets[action.payload.id].results.length

	    }
            return copyState
        }
	case "SET_OFFSET":{
	    if (action.payload.id == null) {
		copyState.active_dataset.offset = 
		    Math.min( Math.max( action.payload.offset , 20), copyState.active_dataset.results.length)
	    } else {
		copyState.datasets[action.payload.id].offset = 
		    Math.min( Math.max( action.payload.offset, 20), copyState.datasets[action.payload.id].results.length  )
	    }
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
    //this.handleChartClick = this.handleChartClick.bind(this);
    this.plotGraph = this.plotGraph.bind(this);
    this.renderLegend = this.renderLegend.bind(this);
  }

  componentDidMount() {
    this.plotGraph()
  }

  handleChartClick(that) {
    console.log('setting handleChartClick')
    var hallmark_codes =
          that.props.metadata[that.props.hallmarks+"_hallmark_codes"]
    var hallmark_codes_arr = _.sortBy( _.keys(hallmark_codes) )
    var hallmark_names_arr = _.map(hallmark_codes_arr, (o) => hallmark_codes[o])
    var data = _.map(hallmark_names_arr, (o) => that.props.data[o])
    
    return function(event) {
	console.log('chart is clicked')	

        var chart = this;    // called in context of chart
	var elements = chart.getElementAtEvent(event);
	
        if (elements && elements.length > 0 && elements[0]){
	    var element = elements[0];
	    var hallmark_code = hallmark_codes_arr[element._index];
	    var hallmark_name = hallmark_names_arr[element._index];
	    
	    that.props.onHallmarkClick(hallmark_code, hallmark_name)
	}
    };

    /*
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
    */


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
		  "query": this.props.title
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
	      "text": this.props.title
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

      options.onClick =  this.handleChartClick(this)      
      

      window.chart1 = new Chart(ctx1, {
	  type: "doughnut",
	  data: chartData1,
	  options: options
      });

      console.log('Chart 1')
      console.log(window.chart1)
      
      //this.handleChartClick()
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


class FileDragDropPanel extends React.Component {

  constructor(props) {
    super(props);

    this.handleDragOver = this.handleDragOver.bind(this);
    this.handleFileSelect = this.handleFileSelect.bind(this);

    this.myRef = React.createRef();
  }

  handleDragOver(evt) {
      evt.stopPropagation();
      evt.preventDefault();
      evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
  }

  handleFileSelect(evt) {
      var that = this
      evt.stopPropagation();
      evt.preventDefault();

      var files = evt.dataTransfer.files; // FileList object.
      console.log('files')
      console.log(files)

      if (files.length > 0 ){
	  var reader = new FileReader();
	  // Read in the image file as a data URL.
	  reader.onload = function(e) {
	      var text = reader.result;
	      console.log(text)
              that.props.handleNewData( text.split(/\n/) )
	  }
	  reader.readAsText(files[0]);
      }
  } 

  componentDidMount() {
      this.myRef.current.addEventListener('dragover', this.handleDragOver, false);
      this.myRef.current.addEventListener('drop', this.handleFileSelect, false);
  }
  
  render() {

    return (
	<div ref={this.myRef} style={{height: '60px', textAlign: 'center', border: '1px dashed #ced4da', 
		     marginBottom: '30px', display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
	    {window.File && window.FileReader && window.FileList && window.Blob ?
	    <h6>Or drop PMID list here <i className="far fa-file"></i></h6> :
	    <h6>Your browser does not support file drag and drop</h6> }
        </div>
    )
  
  }


}






class ComparePanel extends React.Component {

    constructor(props) {
	super(props);
	this.handleChange = this.handleChange.bind(this);
	this.state = {dataset1: null, dataset2: null  }
    }

    handleChange(e,dataset) {
	e.preventDefault();
	var newState = this.state
        newState[dataset] = e.target.value
        this.setState(newState)
    }

    calculatePValueMatrix() {
	var datasets = this.props.datasets
	var activedata = this.props.activedata
    }

    render() {
	return (
	    <div className="row">
		<div className="col">

		    <div>
			<form>
			  <div className="form-row">
			    <div className="form-group col-6">
			      <label htmlFor="inputState">Dataset 1</label>
			      <select id="inputCompare1" className="form-control" value={_.keys(this.props.datasets)[0]} 
				      onChange={(e)=>this.handleChange(e, 'dataset1')}
			      >
				{ _.map(_.keys(this.props.datasets),
					function(o,ind){ return (<option  key={ind}>{o}</option>) })}
			      </select>
			    </div>
			    <div className="form-group col-6">
			      <label htmlFor="inputState">Dataset 2</label>
			      <select id="inputCompare2" className="form-control" value={_.keys(this.props.datasets)[0]}
				      onChange={(e)=>this.handleChange(e,'dataset2')}
			      >
				{ _.map(_.keys(this.props.datasets),
					function(o,ind){ return (<option  key={ind}>{o}</option>) })}
			      </select>
			    </div>
			  </div>
			</form>
		    </div>

		</div>
	    </div>
	)
    }
}
const ReduxedComparePanel = connect(
    (state) => {return { metadata: state.dataR.metadata, 
			 activedata:state.dataR.active_dataset, 
			 datasets: state.dataR.datasets }; },
    (dispatch) => {return {};    
    }
)(ComparePanel)







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
		  },
		  textFile: null
	       	};

    // This binding is necessary to make `this` work in the callback
    this.handleNextPage = this.handleNextPage.bind(this);
    this.handlePrevPage = this.handlePrevPage.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.handleChange = this.handleChange.bind(this);
    this.handleSelectHallmark = this.handleSelectHallmark.bind(this);
    this.handleNewPMIDQry = this.handleNewPMIDQry.bind(this);
    this.downloadPMIDs = this.downloadPMIDs.bind(this)
    this.generateQueryData = this.generateQueryData.bind(this)
  }

  generateQueryData(props,state){
    var data = props.dataset == null ? 
		 _.merge({},state.formVals,_.pick(props.activedata, ['hm','pmids','offset'] )) : 
		 this.props.datasets[dataset],ispaging
    return data
  }

  componentDidUpdate(prevProps, prevState) {
    var newdata = this.props.dataset == null ? this.props.activedata : this.props.datasets[this.props.dataset]
    var olddata = prevProps.dataset == null ? prevProps.activedata : prevProps.datasets[prevProps.dataset]

    console.log('in componentDidUpdate')
    console.log(newdata.hm)
    console.log(olddata.hm)

    if (this.props.dataset != prevProps.dataset){
	var dataset = this.props.dataset
	var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
	if (!data.results && dataset != null){
	    //this.props.runQuery(this.props)
	    this.props.runQuery(this.props.dataset,this.generateQueryData(this.props,this.state))
	}
    } else if (!_.isEqual(newdata.hm , olddata.hm)) {
	console.log('should be running query')
	//this.props.runQuery(this.props)
	this.props.runQuery(this.props.dataset,this.generateQueryData(this.props,this.state))
    } else if (this.props.dataset == null && prevProps.dataset == null &&
	       !_.isEqual(this.props.activedata.pmids, prevProps.activedata.pmids)) {
        console.log('pmids have changed!!!')
        console.log(this.props)
	//this.props.runQuery(this.props)
	this.props.runQuery(this.props.dataset,this.generateQueryData(this.props,this.state))
    }	
  }

  componentDidMount() {
    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
    if (!data.results && dataset != null){
	//this.runQuery(this.props)
	this.props.runQuery(this.props.dataset, this.generateQueryData(this.props,this.state))
    }
  }
	
  handleNextPage(e) {
    e.preventDefault();
    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
    if (data.offset + 20 <= data.results.length){
	this.props.setOffset_(dataset,data.offset + 20)
    } else {
	//this.runQuery(this.props,true)
	this.props.runQuery(this.props.dataset,this.generateQueryData(this.props,this.state), true)
    }
  }

  handlePrevPage(e) {
    e.preventDefault();
    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
    this.props.setOffset_(dataset,data.offset - 20)
  }

  handleClick(e) {
    e.preventDefault();
    var formVals = this.state.formVals
    if (formVals.term.length > 0 ) {

	console.log('Query clicked')
	//this.props.clearcboard_()
	if (this.props.activedata.hasOwnProperty('pmids')) {
	    console.log('clearing active data pmids')
	    this.props.setactivedata_({'pmids':null},false)
	} else {
	    //this.runQuery(this.props)
	    this.props.runQuery(this.props.dataset,this.generateQueryData(this.props,this.state))
	}
    }
  }

  handleChange(key,e) {
    var toMerge = {}
    toMerge[key] = e.target.value

    this.setState(prevState => (  _.merge({},prevState,{ formVals:toMerge} )  ));
  }

  
  handleSelectHallmark(hmcode) {
    console.log('handleSelectHallmark fired!')
    console.log(hmcode)
    var dataset = this.props.dataset
    var setDataRespFn = dataset == null ? this.props.setactivedata_ : 
					  (d,ispaging_) => this.props.addData_(dataset,d,ispaging_)
    setDataRespFn({'hm':hmcode != null ? [hmcode] : []},false)
  }

  handleNewPMIDQry(pmids) {
    console.log('query pmids are')
    console.log(pmids)
    this.props.setactivedata_({'pmids':_.filter(pmids,(o) => o.length > 0 ), term: null},false)
  }

  downloadPMIDs(pmids) {
    var data = new Blob([pmids.join('\n')], {type: 'text/plain'});
    // If we are replacing a previously generated file we need to
    // manually revoke the object URL to avoid memory leaks.
    //if (this.state.textFile !== null) {
    //  window.URL.revokeObjectURL(this.state.textFile);
    //}
    var textFile = window.URL.createObjectURL(data);
    return textFile;
  }


  render() {
    var that = this
    var dataset = this.props.dataset
    var data = dataset == null ? this.props.activedata : this.props.datasets[dataset] 
    


    if (_.isEmpty(data) && dataset == null){
	return (
	    <div className="row">
		<div className="col-md-8 offset-md-2">
		    <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
				      formVals={this.state.formVals}/>
		    <FileDragDropPanel handleNewData={this.handleNewPMIDQry} />
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

    var hallmark_codes = this.props.metadata["full_hallmark_codes"]
    console.log('hallmark_codes')
    console.log(hallmark_codes)
    console.log(data.hm)

    return (
	<div className="row">
	    <div className="col-md-7 order-md-2">
                <div style={{marginTop: '30px', marginBottom: '30px'}}>
                    
		    { dataset == null ?  <ReduxedSearchBox handleClick={this.handleClick} handleChange={this.handleChange} 
                        formVals={this.state.formVals}/> : null }
		    { dataset == null ?  <FileDragDropPanel handleNewData={this.handleNewPMIDQry} /> : null }
                    <div className="d-none d-md-block" style={{marginTop: '30px'}}>
			{ data.results  ?
			   <div>
			       <div style={{padding: '6px', backgroundColor: '#007bff', color: 'white'}}>
			         {data.term ? data.term : 'Searching PubMed IDs'} 
			         {data.pmids ? 
                                     <a href="#" onClick={() => this.downloadPMIDs(data.pmids)}>
				     <i className="fas fa-download"></i></a>  : null} 
				 {data.hm && data.hm.length > 0 ? ' > '+ hallmark_codes[data.hm[0]] + ' ' : ' '}
				 {data.hm && data.hm.length > 0 ?  
				    <a  style={{color: 'white'}}
					href="#" onClick={(e) => { e.preventDefault();that.handleSelectHallmark(null); } } >
					<i className="far fa-times-circle"></i>
				    </a>
				    : null}
			       </div>
			       <div style={{display: 'flex', flexDirection: 'row', justifyContent: 'space-between', padding:5}}>
				<a href="#" onClick={(e) => this.handlePrevPage(e)}>&lt;Prev</a>
				<p>
				    {Math.max(data.offset-20+1,1) + ' to ' + data.offset + 
				    (data.counts ? ' of  ' + data.counts[null] : ''  ) }
				</p>
				<a href="#" onClick={(e) => this.handleNextPage(e)}>Next&gt;</a>
			       </div>
			   </div>
			  : null
			}
                        {data.results ? 
			 _.map(_.slice(data.results, Math.max( data.offset - 20,0),data.offset),function(o,ind){ 
			    return (<ReduxedSearchItem showAddRem={dataset == null} item={o}  key={ind} />) }):
			 null}
                    </div>
		</div>
	    </div>
	    <div className="col-md-5 order-md-1">
		<div style={{marginTop: '30px', marginBottom: '30px'}}>
		    {data.values ? 
			<ReduxedMyChart onHallmarkClick={this.handleSelectHallmark}
					data={data.values} term={data.term} 
					title={data.term?data.term:data.pmids?data.pmids.join(','):'Chart'}
				        hallmarks={data.hallmarks} /> : null }
		</div>
	    </div>
	    <div className="d-md-none">
                <div style={{marginTop: '30px', marginBottom: '30px'}}>
                    <div>
			{ data.results  ?
			   <div>
			       <div style={{padding: '6px', backgroundColor: '#007bff', color: 'white'}}>
			         {data.term ? data.term : 'Searching PubMed IDs'} 
			         {data.pmids ? 
                                     <a href="#" onClick={() => this.downloadPMIDs(data.pmids)}>
				     <i className="fas fa-download"></i></a>  : null} 
				 {data.hm && data.hm.length > 0 ? ' > '+ hallmark_codes[data.hm[0]] + ' ' : ' '}
				 {data.hm && data.hm.length > 0 ?  
				    <a  style={{color: 'white'}}
					href="#" onClick={(e) => { e.preventDefault();that.handleSelectHallmark(null); } } >
					<i className="far fa-times-circle"></i>
				    </a>
				    : null}
			       </div>
			       <div style={{display: 'flex',flexDirection: 'row', justifyContent: 'space-between', padding: 5}}>
				<a href="#" onClick={(e) => this.handlePrevPage(e)}>&lt;Prev</a>
				<p>{Math.max(data.offset-20+1,1) + ' to ' + data.offset + 
				    (data.counts ? ' of  ' + data.counts[null] : ''  ) }</p>
				<a href="#" onClick={(e) => this.handleNextPage(e)}>Next&gt;</a>
			       </div>
			   </div>
			  : null
			}
                        { data.results ? _.map(_.slice(data.results, Math.max( data.offset - 20,0),data.offset),function(o,ind){ 
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
	    setactivedata_ : (activedata,ispaging) => { dispatch(setActiveData(activedata,ispaging)) },
	    setpmcdataid_  : (id, pmcresults)  => {  dispatch(setPMCData(id,pmcresults)) }, 
	    addData_  : (id,data,ispaging)  => {  dispatch(addData(id,data,ispaging)) },
	    setOffset_  : (id,offset)  => {  dispatch(setOffset(id,offset)) },
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
    this.fillParams = this.fillParams.bind(this);
    this.runQuery = this.runQuery.bind(this);
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


  fillParams(data, ispaging) {
    var params = _.pick(data,['term','hm','hallmarks','measure','offset'])
    if (data.hasOwnProperty('pmids')) { 
      params['pmids']=_.filter(data.pmids,(o) => o.length > 0 ).join(','); 
      delete params['term']
    }
    if (params.hasOwnProperty('term')){
      params['q'] = params['term']
      delete params['term']
    }
    params['asjson'] = 1
    return ispaging ? params : _.omit(params, ['offset'])
  }

  runQuery(dataset,data,ispaging) {
	var setactivedata_ = this.props.setactivedata_
	var setpmcdataid_ = this.props.setpmcdataid_
	var addData_ = this.props.addData_

	//var dataset = props.dataset

	/*
	var params = dataset == null ? 
			this.fillParams(_.merge({},this.state.formVals,
			    _.pick(this.props.activedata, ['hm','pmids','offset'] )), ispaging) : 
			this.fillParams(props.datasets[dataset],ispaging)
		    // { q:formVals.term, measure:formVals.measure, hallmarks: formVals.hallmarks, asjson: 1   }
	*/

	var params = this.fillParams( data , ispaging )

	var urlqrystr = ''
	var hallmarks = params.hm
        if (hallmarks && hallmarks.length > 0 ){
	    delete params['hm']
	    console.log(hallmarks)
            urlqrystr = '?' + _.map(hallmarks, (o) => 'hm='+o.toString()   ).join('&')
	}
	if (dataset == null && params.term && params.pmids){
	    delete params['term']
	}
	console.log('running query!')
	var setDataRespFn = dataset == null ? setactivedata_ : (d,ispaging_) => addData_(dataset,d,ispaging_)
	$.get( "/search"+urlqrystr, params , function( data ) { 
	    //setactivedata_(data)
	    delete data['hm']
	    setDataRespFn(data ,ispaging)

	    if (!data.hasOwnProperty('results') || data.results.length == 0){return }

	    var pmids = _.map(data.results, (o) => o.pmid).join(',')	
	    $.getJSON("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id="+pmids+"&retmode=json&tool=crab2&email=tss42@cam.ac.uk", function(data){setpmcdataid_(dataset, data.result)}); 
	}, "json");
	
        if (!ispaging){
	    $.get( "/chartdata", params, function( data ) { 
		setDataRespFn(data[0],false)  //setactivedata_(data[0])
	    }, "json");
	}
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
    var outState = {}
    outState[key] = e.target.value    
    this.setState(outState)
  }

  handleSaveClick(e,type) {
    e.preventDefault();

    //add to the datasets
    if (type == 'query' && this.props.activedata.hasOwnProperty('term')  && 
	this.props.activedata.hasOwnProperty('results') && this.props.activedata.hasOwnProperty('values') ) { 
	this.props.addData_(this.state.queryDatasetName,_.pick(this.props.activedata,['term','hm','hallmarks','measure','offset']))
	this.setState({queryDatasetName: this.generateNewDatasetId('Qry-') })
    }
    else if (type == 'query' && this.props.activedata.hasOwnProperty('pmids')  && 
	this.props.activedata.hasOwnProperty('results') && this.props.activedata.hasOwnProperty('values') ) { 
	this.props.addData_(this.state.queryDatasetName,_.pick(this.props.activedata,['pmids','hm','hallmarks','measure','offset']))
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
		<form className="form-inline">
		    <div className="form-group">
			<input name="datasetname" className="form-control" style={{margin: '3px'}} 
			       value={type == 'query' ? this.state.queryDatasetName : this.state.docsDatasetName} 
			       onChange={(e) => this.handleSaveChange(e,type == 'query' ? 
					'queryDatasetName' : 'docsDatasetName' )} />
			<button type="button" className="form-control btn btn-primary"  style={{margin: '3px'}} 
			    onClick={(e) => this.handleSaveClick(e,type)}>
			    Save
			</button>
			<button type="button"  style={{margin: '3px'}} 
				className="form-control btn btn-secondary" data-dismiss="modal">Cancel</button>
		    </div>
		</form>
	      </div>
	    </div>
	  </div>
	</div>
    )

  }
	
  render() {
    var activedata = this.props.activedata
    
    var save_query_enabled = (this.props.activedata.hasOwnProperty('term') || this.props.activedata.hasOwnProperty('pmids'))  && 
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
					    Main
				    </button>
				</li>
				{ Object.keys(this.props.datasets).length > 0 ?
				<li className="list-inline-item">
				    <button onClick={(e) => this.handleActivePanelClick(e,false)} 
					type="button" 
					className={"btn btn-outline-info"}>
					    Compare
				    </button>
				</li>
				: null }
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
		{ this.state.activepanel !== false ?
		    <ReduxedQueryPanel runQuery={this.runQuery} dataset={this.state.activepanel} /> :
		    <ReduxedComparePanel /> 
		}
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
 
	setactivedata_ : (activedata,ispaging) => { dispatch(setActiveData(activedata,ispaging)) },
	setpmcdataid_  : (id, pmcresults)  => {  dispatch(setPMCData(id,pmcresults)) }, 
	addData_  : (id,data,ispaging)  => {  dispatch(addData(id,data,ispaging)) },
	setOffset_  : (id,offset)  => {  dispatch(setOffset(id,offset)) },
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








//Remaining TODO
//3. implement file drag and drop
//3. export pmids as list
//2. implement compare panel

//5. fix paging for document select / document numbers
//6. implement query save url by session

