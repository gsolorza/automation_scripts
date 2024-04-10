from os import lseek
import requests
import json
from pprint import pprint
import pandas as pd

hostList = []
ipAddr = []

dataFrame = {
    "host": hostList, 
    "ipAddr": ipAddr,
}

def dnaAuth():
    payload = json.dumps({
    "username": "admin",
    "password": "WgU0znN(qhxf"
    })   
    headers = {
    'Content-Type': 'application/json'
    }
    url = "https://172.23.1.10/api/v1/ticket"
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return response.json()["response"]["serviceTicket"]


def getInventory(token):
    url = "https://172.23.1.10/api/v1/network-device"
    payload={}
    headers = {
    'X-Auth-Token': f'{token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    return response.json()["response"]


token = dnaAuth()
deviceList = getInventory(token)

ISR = []
count: int = 0
for device in deviceList:
    series = device["series"]
    print(series)
    hostname = device["hostname"].rstrip('.NAP.local')
    ip = device["managementIpAddress"]
    if "800" in series:
        data = ip
        count += 1
        hostList.append(hostname)
        ipAddr.append(ip)
        with open("inventory.txt", "a+") as wr:
            wr.write(data+"\n")

df = pd.DataFrame(dataFrame)
writer = pd.ExcelWriter("nap-inventory.xlsx", engine="xlsxwriter")
df.to_excel(writer, "nap-inventory")
writer.save()

print(count)