#
# script uses old api version
#
# save the "image" directory in the current directory
#
import json
import os

import requests

user_auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MTc3NjIwMzgsInVzZXJfaWQiOjF9.Pi9w-pj7-obiq78W9UgUXHUgnlE6A4c6ECgKKjiNxus"
headers = {"Authorization": f"Bearer {user_auth_token}"}
url = "http://localhost:8080/exercises/"

current_directory = os.getcwd()
json_path = os.path.join(current_directory, "main_images.json")

payload = []
with open(json_path, "r", encoding="utf-8") as file:
    payload = json.loads(file.read())

for i in range(len(payload)):
    photos = []
    for j in range(len(payload[i]["photos"])):
        path = payload[i]["photos"][j]
        filename = os.path.basename(path)
        file_tuple = ("photos", (filename, open(path, "rb"), "image/jpeg"))
        photos.append(file_tuple)

    del payload[i]["photos"]
    schema_data = json.dumps(payload[i])
    schema = {"schema": schema_data}

    response = requests.post(url, data=schema, files=photos, headers=headers)

    # The loading indicator
    if i % 25 == 0:
        print(response.status_code)
        print(response.json())
