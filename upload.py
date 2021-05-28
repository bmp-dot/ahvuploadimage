import requests
import json
from requests.auth import HTTPBasicAuth
import urllib3
import time
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper
import os


#Suppress cert warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Global vars
image_name = "ImageNameInAHV.qcow2"
image_path = "LocalPathToImage.qcow2"
pc_user = "admin"
pc_password = "xxxxxxxxx"
uri = "https://<PC-IP>:9440/api/nutanix/v3/images"


#Create image UUID on PC
data = {"spec":{"name":image_name,"resources":{"image_type":"DISK_IMAGE"}},"metadata":{"kind":"image"},"api_version":"3.1.0"}
headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
r = requests.post(uri, auth = HTTPBasicAuth(pc_user, pc_password), json=data, headers=headers, verify=False)
image_json = json.loads(r.content)
imageuuid = image_json['metadata']['uuid']


#Upload image on PC
url = uri + "/{}/file".format(imageuuid)
headers = {'Content-Type': 'application/octet-stream;charset=UTF-8', 'accept-encoding': 'gzip, deflate, br', 'Accept': 'application/json'}
print("Upload pending") 
#Delay added to allow UUID create to finish (need to add status check to remove delay in future)
time.sleep(20)
print("Uploading new image:", imageuuid)

#Define file with status bar
file_size = os.stat(image_path).st_size
with open(image_path, "rb") as f:
    with tqdm(total=file_size, unit="B", unit_scale=True, unit_divisor=1024) as t:
      wrapped_file = CallbackIOWrapper(t.update, f, "read")
      r = requests.put(url, auth = HTTPBasicAuth(pc_user, pc_password), data=wrapped_file, headers=headers, verify=False)

if r.ok:
    print("Upload completed successfully!")
else:
    print("Something went wrong!")
