import json
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
import time
import secrets
import jwt
import requests
import shutil
from datetime import datetime


def upload_file(file_name: str, shared_link: bool, sub_folder: str, folder_det: bool, zip: str):
    # Read the config file
    global link
    #config = json.load(open('box_sandbox_config.json'))
    config = json.load(open('box_sandbox_config.json'))

    appAuth = config["boxAppSettings"]["appAuth"]
    privateKey = appAuth["privateKey"]
    passphrase = appAuth["passphrase"]

    # Decrypt the private key using the pass phrase from the file
    key = load_pem_private_key(
      data=privateKey.encode('utf8'),
      password=passphrase.encode('utf8'),
      backend=default_backend(),
    )

    # Create the JWT assertion to authenticate the service and get the access token
    authentication_url = 'https://api.box.com/oauth2/token'

    auth_payload = {
      'iss': config['boxAppSettings']['clientID'],
      'sub': config['enterpriseID'],
      'box_sub_type': 'enterprise',
      'aud': authentication_url,
      'jti': secrets.token_hex(64),
      'exp': round(time.time()) + 45
    }

    keyId = config['boxAppSettings']['appAuth']['publicKeyID']

    assertion = jwt.encode(
      auth_payload,
      key,
      algorithm='RS512',
      headers={
        'kid': keyId
      }
    )

    # Get the access token
    params = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
        'assertion': assertion,
        'client_id': config['boxAppSettings']['clientID'],
        'client_secret': config['boxAppSettings']['clientSecret']
    }
    response = requests.post(authentication_url, params)
    access_token = response.json()['access_token']
    #print(access_token)

    # Read the json file to make API calls
    #payload = json.load(open('jwtconfig_sandbox.json', ))
    payload = json.load(open('jwtconfig_sandbox.json', ))
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    # Get folder details
    if folder_det:
        response = requests.get('https://api.box.com/2.0/folders/1234', headers=headers)
        print(response.json())
    # shared link
    if shared_link:
        response = requests.put('https://api.box.com/2.0/folders/1234?fields=shared_link', headers=headers)
        if response.ok:
            link = response.json()['shared_link']['url']
        else:
            print(response.content)
    # Create a sub folder
    if sub_folder:
        response = requests.post('https://api.box.com/2.0/folders', headers=headers, json=payload['Folder_Create'])
    # Zip the directory
    if zip:
        file_name=file_name+'_'+str(datetime.today().strftime('%Y-%m-%d-%H:%M'))
        shutil.make_archive(file_name, 'zip', zip)
        file_name=file_name+'.zip'
    if file_name:
        # Upload file
        data = {'attributes': '{"name":"file_name", "parent":{"id":"1234"}}'}
        data['attributes'] = data['attributes'].replace("file_name", file_name)
        headers_up = {"Authorization": "Bearer "+access_token}
        # files = [('file', (file_name, open(file_name, 'rb'), 'application/pdf'))]
        files = [('file', (file_name, open(file_name, 'rb'), 'file'))]
        response = requests.post('https://upload.box.com/api/2.0/files/content', headers=headers_up,
                                 data=data, files=files)
        if not response.ok:
            link = ''
            print('file_create: ' + response.text)
    return link
