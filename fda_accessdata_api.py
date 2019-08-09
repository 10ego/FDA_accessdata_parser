from flask import Flask, jsonify, request, make_response
import requests
from custom_fda_parser import accessdata_parser
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.route('/', methods=['GET'])
def default():
	return 'Drugs@FDA data parser API v 0.1'

@app.route('/api/v1/resources/accessdataFDA', methods=['GET'])
def api():
	try:
		if "search" in request.args:
			api = accessdata_parser(request.args['search'])
			response = api.build_productlist()
			if response == {}:
				print('404')
				status_code = 404
				response['message'] = "No results found for {}".format(request.args['search'])
			elif len(response)>0:
				print('200')
				status_code = 200

			else:
				print('500')
				response['message'] = "Internal server error"
				status_code = 500
		else:
			print('400')
			status_code = 400
			return make_response("Bad request error", 400)

		response['meta'] = {'requester':'hc','timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
		print("DEBUGGING MATCH KEYS?:", response.keys())
		return make_response(jsonify(response), status_code)
	except Exception as e:
		print("Exception caught:", type(e), e.args)
		return make_response("Bad request error", 400)

if __name__ == "__main__":
	app.run()
