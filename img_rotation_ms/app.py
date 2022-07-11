from flask import Flask, request, send_file, jsonify
from PIL import Image
from io import BytesIO
import os
import requests

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "Hello, World!"


@app.route("/rotation", methods=['POST'])
def rotation():
    img_file = request.files.get('image')


    img_ext = ['png', 'jpg', 'jpeg', 'gif']
    file_name = img_file.filename
    extension = file_name.split('.')[-1]
    if extension.lower() not in img_ext:
        return jsonify({'error': 'File is not a typical image'}), 400

    img = Image.open(img_file)

    if img is None:
        return jsonify({'error': 'No image found'}), 400

    try:
        angle = int(request.query_string)
    except:
        return jsonify({'error': 'Unable to convert request to an angle'}), 400
    img = img.rotate(angle, expand=True)

    new_file = BytesIO()
    img.save(new_file, 'PNG')
    new_file.seek(0)

    return send_file(new_file, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 7534))
    app.run(host='0.0.0.0', port=port, debug=True)
