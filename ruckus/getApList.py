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


# with open("none_static_aps", "w+") as noneStatic:
#   noneStatic.write("OUTPUT\n")

with open("host.txt", "w+") as host:
    host.write("")

with open("noipap.txt", "w+") as host:
    host.write("")

no_ip: int = 0
for ap in tqdm(apList, ascii=True):

    apMac = ap.get("mac")
    url = f"https://172.20.1.11:8443/wsg/api/public/v6_0/aps/{apMac}"
    response = s.get(url, headers=headers, verify=False)
    ip = response.json().get("network").get("ip")
    apName = response.json().get("name")
    if ip:
        with open("host.txt", "a+") as host:
          host.write(f"{ip}\n")
    else:
        urlOpsInfo = f"https://172.20.1.11:8443/wsg/api/public/v6_0/aps/{apMac}/operational/summary"
        response = s.get(urlOpsInfo, headers=headers, verify=False)
        ip = response.json().get("ip")
        with open("noipap.txt", "a+") as host:
          host.write(f"{ip}\n")

   
    print(f"{apName} - {ip}")
 
    