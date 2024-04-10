import requests
import json
from pprint import pprint
from tqdm import tqdm

url = "https://172.20.1.11:8443/wsg/api/public/v6_0/session"

payload = json.dumps({
  "username": "",
  "password": "",
  "timeZoneUtcOffset": "+08:00"
})
headers = {
  'Content-Type': 'application/json'
}

s = requests.Session()
response = s.post(url, headers=headers, verify=False, data=payload)

url = "https://172.20.1.11:8443/wsg/api/public/v6_0/aps?listSize=400"

payload = ""
headers = {
  'Content-Type': 'application/json'
}

response = s.get(url, headers=headers, verify=False)

apList = response.json().get("list")

for ap in tqdm(apList, ascii=True):
    apMac = ap.get("mac")
    payload = json.dumps({
      "apLoginName": "admin",
      "apLoginPassword": "gX9qO!2h9!9b",
    })
    url = f"https://172.20.1.11:8443/wsg/api/public/v6_0/aps/{apMac}/login"
    response = s.patch(url, headers=headers, data=payload, verify=False)
    pprint(response.status_code)
    
 
    