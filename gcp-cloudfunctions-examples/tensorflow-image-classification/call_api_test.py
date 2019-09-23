import requests
import base64

image_path = 'images/test.png'
api_uri = "https://us-central1-it-270-252419.cloudfunctions.net/classify-risk-it270"

with open(image_path, "rb") as fp:
    encoded_image_bytes = base64.b64encode(fp.read())
encoded_image_str = encoded_image_bytes.decode('utf-8')

request = {'image': encoded_image_str}

response = requests.post(api_uri, json=request)
print(response.json())

# resp = response.json()['image']
# img_bytes = resp.encode('utf-8')
# img = base64.b64decode(img_bytes)

# with open('test.jpg', 'wb') as fp:
#     fp.write(img)
