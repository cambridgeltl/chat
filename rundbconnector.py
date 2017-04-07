#!/usr/bin/env python

from dbconnector import app
from dbconnector import config

if config.DEBUG:
    app.run(debug=True, port=config.PORT, use_reloader=False)
else:
    app.run(host='0.0.0.0', port=config.PORT)
