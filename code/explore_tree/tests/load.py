import requests
import json
import os
import datetime

USER = "admin"
PSWD = "admin"
MDCS_URL = "http://127.0.0.1:8000"

templates = {
'test':'test.xsd',
}

templates_data = {
	'test': ['instance1.xml', 'instance2.xml', 'instance3.xml', 'instance4.xml', 'instance5.xml'],
}

template_ids = {
	'test': None,
}


# Add the templates
for template_name, template_path in templates.iteritems():
	file = open(os.path.join('templates', template_path),'r')
	templateContent = file.read()
	url = MDCS_URL + "/rest/templates/add"   
	data = {"title": template_name, 
			"filename": template_path,
			"content": templateContent}
	r = requests.post(url, data, auth=(USER, PSWD))   
	response = json.loads(r.text)

	template_ids[template_name] = response['_id']['$oid']
	
	status = 'succeeded' if r.status_code == 201 else 'failed'
	print template_name + ' upload ' + status

	
# Add the data
url = MDCS_URL + "/rest/curate"   
for template_name, data_list in templates_data.iteritems():
	for data_name in data_list:
		file = open(os.path.join('data', data_name),'r')
		fileContent = file.read()
		data_to_send = {"title": data_name, 
						"schema": str(template_ids[template_name]),
						"content": fileContent}
		r = requests.post(url, data_to_send, auth=(USER, PSWD))

		status = 'succeeded' if r.status_code == 201 else 'failed'
		print data_name + ' upload ' + status + '(' + str(r.status_code) + ')'
		if r.status_code != 201:
			print r.text
