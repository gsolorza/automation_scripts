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

for device in deviceList:
    pprint(device)
    break
    series = device["series"]
    hostname = device["hostname"]
    ip = device["managementIpAddress"]
    # if "4300" in series:
    #     ISR.append(device["serialNumber"])
    # data = f"{hostname} ansible-host={ip}"
    data = f"{ip}"
    # print(data)
    hostList.append(hostname)
    ipAddr.append(ip)
    with open("inventory.txt", "w+") as wr:
        wr.write(data)

df = pd.DataFrame(dataFrame)
writer = pd.ExcelWriter("nap-inventory.xlsx", engine="xlsxwriter")
df.to_excel(writer, "nap-inventory")
writer.save()