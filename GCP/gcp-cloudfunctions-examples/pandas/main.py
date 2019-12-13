# Call to create cloud function: gcloud functions deploy pandas_test_function --runtime python37 --trigger-http

import pandas as pd
from io import StringIO

def pandas_test_function(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
    """
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'data' in request_json:
        csv_data = request_json['data']
    elif request_args and 'data' in request_args:
        csv_data = request_args['data']
   
    df = pd.read_csv(StringIO(csv_data), sep=";")

    return df.iloc[0].to_string()