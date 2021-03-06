# Atlas Scientific Web 
Atlas Scientific Web is a lightweight Rest API and Web UI for sampling and managing Atlas Scientific embedded solutions. At this time, hardware must be in a I2C configuration and running unix based operating system.

# Currently Supported Hardware
- [EZO-pH Circuit](https://www.atlas-scientific.com/circuits/ezo-ph-circuit/)
- [EZO-ORP Circuit](https://www.atlas-scientific.com/circuits/ezo-orp-circuit/)
- [EZO-DO Circuit](https://www.atlas-scientific.com/circuits/ezo-dissolved-oxygen-circuit/)
- [EZO-EC Circuit](https://www.atlas-scientific.com/circuits/ezo-conductivity-circuit/)
- [EZO-CO2 Circuit](https://www.atlas-scientific.com/probes/ezo-co2-embedded-ndir-carbon-dioxide-sensor/)
- [EZO-RTD Circuit](https://www.atlas-scientific.com/circuits/ezo-rtd-temperature-circuit/)

# Verified to work with
In addition to comprehensive unit test coverage, all supported EZO circuit are verified to work with
- Raspberry PI 3 model b+
- Raspbian Buster Lite
- Python 3.7
- [Tentacle T3 for Raspberry Pi](https://www.whiteboxes.ch/shop/tentacle-t3-for-raspberry-pi/)

# Installing from Wheel package
The `atlas_scientific_web` pip package in not published at this time, however a wheel package can be built from source.

## Building Wheel from source 
To build from source python 3.7 and pipenv are required. 

Pull source code either by downloading as a zip from github, or clone the git repo with,
```
git clone https://github.com/jamesjharper/atlas-scientific-web.git
cd atlas-scientific-web
```

Insure required packages are installed with,
```
pipenv install -dev
```

Build package with,
```
pipenv run package
```

Output wheel package will be written to `dist/atlas_scientific_web-0.1.0-py3-none-any.whl`

## Running Wheel on target device
Target device will require python 3.7 installed. 

Install waitress with,
```
pip install waitress
```

Copy wheel to target device and install with,
```
pip install atlas_scientific_web-0.1.0-py3-none-any.whl
```

start web service using waitress with 
```
`waitress-serve --listen=localhost:8080 --call 'atlas_scientific_web:create_app'`
```

# Installing from source
To run from source python 3.7 and pipenv are required. 

Pull source code either by downloading as a zip from github, or clone the git repo with,
```
git clone https://github.com/jamesjharper/atlas-scientific-web.git
cd atlas-scientific-web
```

Insure required packages are installed with,
```
pipenv install
```

## Running as prod
For typically applications, alway run `atlas_scientific_web` as prod using a WSGI server such as `waitress`.

Install waitress with,
```
pip install waitress
```

To start the web service with 
```
pipenv run serve_prod
```

## Running as dev
For development and hardware debugging, `atlas_scientific_web` can be run using `flask`. Flask is not intended for production environments. Flask its not advised to be used with `atlas_scientific_web` in multi client environments due to the long running nature of requests to Atlas Scientific embedded devices. 

To start the web service with 
```
pipenv run serve_dev
```

# Web UI Development
To develope Web UI source node.js is required. 

Installing required packages
```
npm install --no-optional
```

Bundling Web UI
```
npm run build
```

# API Development
To develope Server API source python 3.7 and pipenv are required. 

Installing required packages
```
pipenv install -dev
```

Run unit tests 
```
pipenv run unittests
```

Run locally 
```
pipenv run serve_dev
```
