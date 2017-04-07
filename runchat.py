#!/usr/bin/env python

from chat import app
from chat import config

if config.DEBUG:
    # use_reloader=False prevents double init in debug mode
    # (http://stackoverflow.com/a/9476701)
    app.run(debug=True, port=config.PORT, use_reloader=False)
else:
    app.run(host='0.0.0.0', port=config.PORT)
