from rest_framework.views import exception_handler
import re
def parse(value):
	if value[0].startswith('This field'):
		value[0] = value[0][len('This field'):]
	if value[0].startswith('Invalid pk'):
		m = re.search('- object',value[0])
		value[0] = value[0][m.end():]
	if value[0].startswith('Time'):
		value[0] = value[0][len('Time'):]
	if value[0].startswith('JSON parse error'):
		value[0] = 'Parameters not in JSON format'
	if value[0].endswith('are allowed.'):
		value[0] = value[0][:4].lower()+value[0][4:]
	return value
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    if response is not None:
    	for field, value in response.data.items():
    		if field == 'non_field_errors':
    			errors = "{}".format("".join(parse(value)))
    		elif field =='detail':
    			errors = "{}".format("".join(parse(value)))
    		elif value[0].endswith('are allowed.'):
    			errors = "In {} {}".format(field.replace('_',' '), " ".join(parse(value)))
    		else:
    			errors = "{}{}".format(field.replace('_',' '), " ".join(parse(value)))
    		
    		break

    	for field, value in response.data.items():
    		if type(value) is list:
    			if value[0] == ' is required.':
    				errors = 'Parameter missing.'
    				break

    	response.data = {}
    	response.data['message'] = errors
    	if response.status_code in [401,404,400,403,405]:
    		response.data['success'] = False
    	else:
    		response.data['success'] = True
    	if response.data.get('detail'):
    		response.data['message'] = response.data.get('detail')
    		response.data.pop('detail')
    	return response