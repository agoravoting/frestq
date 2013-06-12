#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of frestq.
# Copyright (C) 2013  Eduardo Robles Elvira <edulix AT wadobo DOT com>

# election-orchestra is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# election-orchestra  is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with election-orchestra.  If not, see <http://www.gnu.org/licenses/>.

import logging
import argparse
from fscheduler import FScheduler

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

### configuration

# debug, set to false on production deployment
DEBUG = True

# database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'

# own certificate, empty if there isn't any
SSL_CERT_STRING = ''

# queues root url
ROOT_URL = 'http://localhost:5000/api/queues'

# import custom settings if any
try:
    from custom_settings import *
except:
    pass

# boostrap our little application
app.config.from_object(__name__)
app.config.from_envvar('FRESTQ_SETTINGS', silent=True)
db = SQLAlchemy(app)
import models

from api import api
from user_api import *
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(user_api, url_prefix='/user')

from protocol import *

def get_scheduler():
    if not hasattr(FScheduler, "instance"):
        setattr(FScheduler, "instance", FScheduler())
    return FScheduler.instance

def run_app(config_object=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--createdb", help="create the database", action="store_true")
    args = parser.parse_args()
    if args.createdb:
        print "creating the database"
        from app import db
        db.create_all()
        return

    if config_object:
        app.config.from_object(config_object)
    get_scheduler().start()
    app.run(threaded=True, port=app.config.get('SERVER_PORT', None), use_reloader=False)

if __name__ == "__main__":
    run_app()