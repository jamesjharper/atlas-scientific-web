
import os
import logging
import sys

from .device_routes import add_device_routes
from flask import Flask, request
from flask_restx import Api

from i2c import I2CBus

def config_logging():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def logging_application_banner():
    logging.info('')
    logging.info('========================')
    logging.info('I2C Microserverice start')
    logging.info('========================')
    logging.info('')

def create_app(i2cbus =I2CBus()): 
    config_logging()
    logging_application_banner()

    app = Flask(__name__)
    api = Api(app, version='1.0', title='I2C Microserverice',
        description='A description of a microserverice',
    )

    @app.before_request
    def log_request_info():
        app.logger.debug('\n[%s] %s\nBody:\n%s', request.method , request.path, request.get_data())

    api.add_device_routes(i2cbus)

    return app