import React from 'react';

const testData = [
  {type: "ORP", samples: [{ value: "141", symbol: "mV"}]},
  {type: "PH", samples: [{ value: "7.1", symbol: ""}]},
  {type: "RTD", samples: [{ value: "30", symbol: ""}]},
  {type: "EC", samples: [{ value: "904", symbol: "uS"}]},
  {type: "DO", samples: [{ value: "5.0", symbol: "mg/L"}, { value: "53", symbol: "%"}]},
];

class App extends React.Component {
  state = {
    devices: testData,
  };
  
	render() {
  	return (
    	<div>
    	  <div className="header">{this.props.title}</div>
        <DeviceList devices={this.state.devices} />
    	</div>
    );
  }	
}

const DeviceList = (props) => (
	<div>
  	{props.devices.map(device => <Device {...device}/>)}
	</div>
);

class Device extends React.Component {
  render() {
  	const device = this.props;
  	return (
    	<div>
        <h1 className={'p-3 mb-2 text-white ' + device.type.toLowerCase() + '_device'}>{device.type} : 
          {
            device.samples
                  .map(sample => <DeviceSample {...sample}/>)
                  .reduce((prev, curr) => [prev, ' ', curr])
          }
        </h1>
    	</div>
    );
  }
}

const DeviceSample = (props) => {
  if (props.symbol) {
    return (<React.Fragment>{props.value} {props.symbol}</React.Fragment>);
  } 
  return (<React.Fragment>{props.value}</React.Fragment>);
}

  
  

export default App;
