import requests
import json
import xml.etree.ElementTree as xmlET
from xml.dom import minidom
import logging


def postToBuyWays(config, xmlFile):
    logging.info("Attempting Post to BuyWays...")

    with open(config, 'r') as config_file:
        conf = json.load(config_file)
        url = conf["buyWaysURL"]
        batch_group = conf["batchGroup"]
    with open(xmlFile, 'r') as xml_file:
        data = xml_file.read()
    headers = {'Content-Type': 'application/xml',
                'Accept': '*/*',
                'Accept-Encoding': 'gzip, deflate, br'}
    request = requests.post(url, headers=headers, data=data.encode('utf-8'))
    if request.status_code >= 300:
        raise Exception(f"Response Status code: {str(request.status_code)}{str(request.reason)}")
    response = xmlET.ElementTree(xmlET.fromstring(request.content))
    response.write(f'postResults/{batch_group}/{xmlFile[-23:-4]}_post_results.xml', encoding='utf-8')
    response_text = (response
                        .find("ResponseMessage")
                        .find("Status")
                        .find("StatusText").text.strip()
                        .replace("(","\n")
                        .replace(")", "")
                        .replace(",",";", 1)
                        .replace(",","\n")
                        .replace(".", "\n")
                        .replace("Counts:","\n"))
    response_status = (int(response.find('ResponseMessage').find('Status').find('StatusCode').text.strip()))
    
    xml_string = minidom.parseString(request.content)
    xml_string = xml_string.toprettyxml(indent="   ")
    logging.info("Post Complete! see post results file for details.")
    return(f'Post Complete!\nUpload Status: {response_status}\n{response_text}\n\nSee post results file for details')