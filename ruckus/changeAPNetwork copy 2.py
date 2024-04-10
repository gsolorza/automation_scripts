import requests
import json
from pprint import pprint
from tqdm import tqdm

url = "https://172.20.1.11:8443/wsg/api/public/v6_0/session"

payload = json.dumps({
  "username": "netvoix@nap.local",
  "password": "gX9qO!2h9!9b",
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


# with open("none_static_aps", "w+") as noneStatic:
#   noneStatic.write("OUTPUT\n")

for ap in tqdm(apList, ascii=True):
    apMac = ap.get("mac")
    url = f"https://172.20.1.11:8443/wsg/api/public/v6_0/aps/{apMac}"
    response = s.get(url, headers=headers, verify=False)
    network = response.json().get("network")
    apName = response.json().get("name")
    if network.get("ipType") == "Static":
        network["primaryDns"] = "10.88.0.20"
        network["secondaryDns"] = "10.92.0.20"
        netUrl = f"https://172.20.1.11:8443/wsg/api/public/v6_0/aps/{apMac}/network"
        s.patch(netUrl, headers=headers, data=json.dumps(network), verify=False)
    # if network.get("ipType") != "Static":
    #   with open("none_static_aps", "a+") as noneStatic:
    #      noneStatic.write(apName)
    #      noneStatic.write(json.dumps(network))
    #      noneStatic.write("\n")
    
 
    