from flask import Flask, request, jsonify
from PIL import Image
import numpy as np
import uuid
import os
from image_utils import preprocess_image, extract_text_from_image

app = Flask(__name__)

@app.route('/ocr', methods=['POST'])
def ocr():
    image = request.files['image']
    file_extension = os.path.splitext(image.filename)[1]
    filename = str(uuid.uuid4()) + file_extension
    image_path = os.path.join('pre_process','input', filename)
    image.save(image_path)
    image=preprocess_image(filename)
    if not image:
        os.remove(image_path)
        return jsonify({'error':'not able to pre process image'})
    os.remove(image_path)
    return jsonify(extract_text_from_image(filename))


@app.route('/dhiva', methods=['POST'])
def dhiva():
    return jsonify({"dhiva":"Ahhhh! you got mee!"})

if __name__ == '__main__':
    app.run(host='192.168.1.3',debug=False)