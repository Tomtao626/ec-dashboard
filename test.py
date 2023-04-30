import base64
image_path = r"/Users/tao626/Documents/workspaces/pywork/ec-dashboard/image.1.jpg"
with open(image_path,'rb')as f:
    base64_data = base64.b64encode(f.read())
    print(str(base64_data))