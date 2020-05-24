import React from 'react';

class App extends React.Component {
	render() {
  	return (
    	<div>
    	  <div className="header">{this.props.title}</div>
        <DeviceList />
    	</div>
    );
  }	
}

class DeviceList extends React.Component {

  constructor() {
    super()
    this.state = { devices: [] }
  }

  componentDidMount() {
    fetch('/api/device')
      .then(result => result.json())
      .then(result => this.setState({ devices: result }));
  }

  render() {
  	return (
      <div>
        {this.state.devices.map(device => <Device {...device}/>)}
      </div>
    );
  }
}

class Device extends React.Component {

  constructor() {
    super()
    this.state = { samples: [
        {
          'value': '...',
          'symbol': ''
        }
      ] 
    }
  }

  componentDidMount() {
    this.sampleDevice()
    this.timer = setInterval(() => this.sampleDevice(), 1000);
  }

  componentWillUnmount() {
    clearInterval(this.timer)
    this.timer = null;
  }

  sampleDevice() {
    fetch('/api/device/' + this.props.address + '/sample')
      .then(result => result.json())
      .then(result => this.setState({ samples: result }));
  }

  render() {
  	const device = this.props;
  	return (
    	<div>
        <h1 className={'p-3 mb-2 text-white ' + device.device_type.toLowerCase() + '_device'}>{device.device_type} : 
          {
            this.state.samples
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
