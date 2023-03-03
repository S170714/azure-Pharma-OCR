import os
import io
import json
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import requests
from PIL import Image,ImageDraw,ImageFont

credentials  = json.load(open('credentials.json'))
API_KEY = credentials ['API_KEY']
ENDPOINT = credentials ['ENDPOINT']

cv_client =ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(API_KEY))

image_url = 'https://user-images.githubusercontent.com/8099731/29282977-6b5300f2-8157-11e7-9489-238c83481edc.jpg'

response = cv_client.read(url = image_url, language='en', row= True)
operationLocation = response.headers['Operation-Location']
operation_id = operationLocation.split('/')[-1]
result = cv_client.get_read_result(operation_id)

print(result)
print(result.status)
print(result.analyze_result)

if result.status == OperationStatusCodes.succeeded:
    read_results = result.analyze_result.read_results
    for analyzed_result in read_results:
        for line in analyzed_result.lines:
            print(line.text) 
            for word in line.words:
                print('Words:')
                print(word.text)     
