""" 
DEPLOY INSTRUCTIONS:

# get list of your projects in google cloud
gcloud config list

# switch to the project where you want to deploy the cloud function (if not selected yet)
gcloud config set project my-project

# deploy it (using the following instruction, the function handler() ill be executed when calling the cloud function )
gcloud functions deploy handler --runtime python37 --trigger-http --memory 2048

"""

import tensorflow as tf
from tensorflow.keras import datasets, layers, models
from google.cloud import storage
import numpy as np
import cv2
import base64
from flask import jsonify

# keep model as global varibale so we don't have to reload it in case of warm invocations
model = None

IMG_SIZE = 160
IMG_SHAPE = (IMG_SIZE, IMG_SIZE, 3)
NR_CLASSES = 3


def create_model():
  model = models.Sequential()
  model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=IMG_SHAPE))
  model.add(layers.MaxPooling2D((2, 2)))
  model.add(layers.Conv2D(64, (3, 3), activation='relu'))
  model.add(layers.MaxPooling2D((2, 2)))
  model.add(layers.Conv2D(64, (3, 3), activation='relu'))

  model.add(layers.Flatten())
  model.add(layers.Dense(64, activation='relu'))
  model.add(layers.Dense(NR_CLASSES, activation='softmax'))
  
  model.compile(optimizer="adam", 
              loss='sparse_categorical_crossentropy', 
              metrics=['accuracy'])
  return model


def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(source_blob_name)

    blob.download_to_filename(destination_file_name)

    print('Blob {} downloaded to {}.'.format(
        source_blob_name,
        destination_file_name))

def preprocess_image(image):
    image = tf.image.decode_jpeg(image, channels=3)
    image = tf.image.resize(image, [IMG_SIZE, IMG_SIZE]).numpy()
    return (image/127.5-1)[np.newaxis,:,:]

def load_and_preprocess_image(path):
    image = tf.io.read_file(path)
    return preprocess_image(image)

def handler(request):
    global model
    classes = {'dry_grass': 0, 'green_grass': 1, 'random': 2}
    class_names = ['dry_grass', 'green_grass', 'random']

    # Model load which only happens during cold starts
    if model is None:
        download_blob('riesgo-tf-model', 'cp-0015.ckpt.index', '/tmp/cp-0015.ckpt.index')
        download_blob('riesgo-tf-model', 'cp-0015.ckpt.data-00000-of-00002', '/tmp/cp-0015.ckpt.data-00000-of-00002')
        download_blob('riesgo-tf-model', 'cp-0015.ckpt.data-00001-of-00002', '/tmp/cp-0015.ckpt.data-00001-of-00002')
        model = create_model()
        model.load_weights('/tmp/cp-0015.ckpt')
        
    # Load image from request
    request_json = request.get_json(silent=True)
    request_args = request.args

    if not request_json or 'image' not in request_json:
        return jsonify({"response" : "Invalid request. Please send a JSON in the format: {'image': image_bytes}"})

    img_string = request_json['image']
    img_bytes = img_string.encode('utf-8')
    img = base64.b64decode(img_bytes)

    tmp_path = '/tmp/tmp.jpg'
    with open(tmp_path, 'wb') as fp:
        fp.write(img)
    
    image = load_and_preprocess_image(tmp_path)

    # Run predictions
    predictions = model.predict(image)
    print(predictions)
    print("Image is "+class_names[np.argmax(predictions)])
    
    return jsonify({"response" : class_names[np.argmax(predictions)]})


def offline_test():
    classes = {'dry_grass': 0, 'green_grass': 1, 'random': 2}
    class_names = ['dry_grass', 'green_grass', 'random']

    model = create_model()
    model.load_weights('model/cp-0015.ckpt')
    
    image = load_and_preprocess_image('images/dry2.jpg')
    predictions = model.predict(image)
    print(predictions)
    print("Image is "+class_names[np.argmax(predictions)])
    
    return class_names[np.argmax(predictions)]


if __name__ == '__main__':
    offline_test()