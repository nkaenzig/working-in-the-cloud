import requests
import json

url = "https://us-central1-shining-expanse-249017.cloudfunctions.net/pandas_test_function"
headers = {
    'Content-Type': 'application/json',
}

with open("test.csv") as fp:
    test_data = fp.read()

data = json.dumps({"data" : test_data})

response = requests.post(url, headers=headers, data=data, allow_redirects=True)

print(response.status_code, response.reason)
print(response.text)