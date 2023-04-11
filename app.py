from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import uuid
import os
import base64
from io import BytesIO
from image_utils import preprocess_image, extract_text_from_image

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    print("Debug")
    data = request.get_json()
    print("data")
    image_bytes = base64.b64decode(data['image'])
    image_buffer = BytesIO(image_bytes)
    img = Image.open(image_buffer)
    print("image")
    filename = str(uuid.uuid4()) + '.jpeg'
    image_path = os.path.join('pre_process','input', filename)
    img.save(image_path)
    img_crop = preprocess_image(filename)
    if not img_crop:
        os.remove(image_path)
        return jsonify({'content':'not able to pre process image'})
    temp = jsonify(extract_text_from_image(filename))
    os.remove(image_path)
    return temp


@app.route('/dhiva', methods=['POST'])
def dhiva():
    print("Testing...")
    data = request.get_json()
    image_bytes = base64.b64decode(data['image'])
    image_buffer = BytesIO(image_bytes)
    img = Image.open(image_buffer)
    img.save('output.jpg')
    content = 'fuck you bitch'
    response = {'content':content}
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='192.168.1.12',debug=False)
