# Drugs@FDA parser

Source FDA page: (https://www.accessdata.fda.gov/scripts/cder/daf/)

Microservice Flask api served from fda_accessdata_api.py.

E.g. GET request: "curl '127.0.0.1:5000/api/v1/resources/accessdataFDA?search={DRUG_NAME}'"

## Demo service
https://secure-forest-17589.herokuapp.com/api/v1/resources/accessdataFDA?search=oxycet

Supported on Python 3.5+
