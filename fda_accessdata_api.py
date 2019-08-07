from flask import Flask, jsonify, request
import requests
from custom_fda_parser import accessdata_parser

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET'])
def default():
	return 'Drugs@FDA data parser API v 0.1'

@app.route('/api/v1/resources/accessdataFDA', methods=['GET'])
def api():
	if "search" in request.args:
		api = accessdata_parser(request.args['search'])
		return jsonify(api.build_productlist())

app.run()
