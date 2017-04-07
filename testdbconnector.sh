#!/bin/bash

# Minimal DB connector test.

# NOTE: execute rundbconnector.py and wait for the message "Running on
# http://..." before running this.

# Total counts
curl 'http://127.0.0.1:5002/hallmarkcount?q=p53'

# Counts for various queries
for q in p53 Akt THISWONTMATCH; do
    curl 'http://127.0.0.1:5002/hallmarkcount?q='"$q"
done
