import requests
import json
import xml.etree.ElementTree as xmlET
from xml.dom import minidom


def postToBuyWays(config, xmlFile):
    try:
        with open(config, 'r') as config_file:
            conf = json.load(config_file)
            url = conf["buyWaysURL"]
            batch_group = conf["batchGroup"]
        with open(xmlFile, 'r') as xml_file:
            data = xml_file.read()
        headers = {'Content-Type': 'application/xml',
                   'Accept': '*/*',
                   'Accept-Encoding': 'gzip, deflate, br'}
        request = requests.post(url, headers=headers, data=data)
        if request.status_code >= 300:
            raise Exception(f'Post Status: {request.status_code}')
        response = xmlET.ElementTree(xmlET.fromstring(request.content))
        response.write(f'postResults/{batch_group}/{xmlFile[-23:-4]}_post_results.xml')
        response_text = (response
                         .find("ResponseMessage")
                         .find("Status")
                         .find("StatusText").text.strip())
        response_status = (int(response.find('ResponseMessage').find('Status').find('StatusCode').text.strip()))

        if response_status >= 300:
            xml_string = minidom.parseString(request.content)
            xml_string = xml_string.toprettyxml(indent="   ")
            print(xml_string)
            raise ValueError(f'Upload Status: {response_status}\n'
                             f'Upload Response Text: {response_text}\n')
        elif response_status == 200:
            return 0
    except Exception as e:
        raise e
