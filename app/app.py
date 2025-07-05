import os
from chalice import Chalice, Response, CORSConfig
import json 
import urllib3

app = Chalice(app_name='input')


# Configure CORS settings according to the deployment environment
# TODO: Replace the localhost URL with the URL of your production front-end
cors_config = CORSConfig(
    allow_origin='https://staticwebsource.s3.amazonaws.com',
    allow_headers=['Content-Type', 'X-Amz-Date', 'Authorization', 'X-Api-Key', 'X-Amz-Security-Token', 'X-Amz-User-Agent'],
    max_age=600,
    allow_credentials=True
)

@app.route('/predict', methods=['POST'], cors=cors_config)
def predict():
    request = app.current_request
    data = request.json_body

    # url = "https://hh3p9jsfw3.execute-api.us-east-1.amazonaws.com/stage52/predict"
    url = "https://nx6v3z9dg3.execute-api.us-east-1.amazonaws.com/stage58/predict"

    headers = {'Content-Type': 'application/json'}

    http = urllib3.PoolManager()
    encoded_data = json.dumps(data).encode('utf-8')
    response = http.request('POST', url, body=encoded_data, headers=headers)
    
    
    prediction = json.loads(response.data.decode('utf-8'))
    
    num = float(prediction['prediction'])
    
    result = 0
    
    if num <= 0.83:
        result = 0
    elif  0.83 <num <= 0.87:
        result = 1
    else:
        result = 2
    
    return Response(
        body={"prediction": result,
             },
        headers={'Content-Type': 'application/json'},
        status_code=200
    )

