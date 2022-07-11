import requests
import shutil

local = 'http://192.168.0.21:7777'

img_file = {'image': open('test_image.jpg', 'rb')}
r = requests.post(local + '/transform?90', files=img_file)
if r.status_code == 200:
    path = 'test_result.jpg'
    with open(path, 'wb') as f:
        f.write(r.content)
