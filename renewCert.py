import requests
import json
from pprint import pprint
import sys
import getpass

hostList = []
ipAddr = []

userName = sys.argv[1]
password = getpass.getpass(prompt="Provide password to connect to APIC-EM: ")
serialNumber = sys.argv[2]

dataFrame = {
    "host": hostList,
    "ipAddr": ipAddr,
}

"""
{
      "platformId": "C892FSP-K9",
      "serialNumber": "FJC2131L4MW",
      "trustProfileName": "sdn-network-infra-iwan",
      "entityName": "POLY-Chihuahua"	
}
"""


def builTrustPoint(deviceData: dict[str, str]):
    fqdn = deviceData.get("entityName")
    platform = deviceData.get("platformId")
    serialNumber = deviceData.get("serialNumber")
    trustpoint: str = f"""
    crypto pki trustpoint sdn-network-infra-iwan
    enrollment url http://173.252.189.173:80/ejbca/publicweb/apply/scep/sdnscep
    fqdn {fqdn}
    subject-name CN={platform}_{serialNumber}_sdn-network-infra-iwan
    vrf IWAN-TRANSPORT-1
    revocation-check none
    rsakeypair sdn-network-infra-iwan
    auto-enroll 80 regenerate
    """
    for line in trustpoint.split("\n"):
        print(line)


def dnaAuth():
    payload = json.dumps({"username": userName, "password": password})
    headers = {"Content-Type": "application/json"}
    url = "https://172.23.1.10/api/v1/ticket"
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=False
    )
    return response.json()["response"]["serviceTicket"]


def getDeviceId(token, serialNumber):
    url = f"https://172.23.1.10/api/v1/trust-point/serial-number/{serialNumber}"
    payload = {}
    headers = {"X-Auth-Token": f"{token}", "Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    data = response.json()["response"]
    deviceData = data["id"]
    return deviceData


def getDeviceInfo(token, serialNumber):
    url = f"https://172.23.1.10/api/v1/network-device/serial-number/{serialNumber}"
    payload = {}
    headers = {"X-Auth-Token": f"{token}", "Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    data = response.json()["response"]
    hostname = data["hostname"].lower().rstrip(".nap.local")
    deviceData = {
        "platformId": data["platformId"],
        "serialNumber": data["serialNumber"],
        "trustProfileName": "sdn-network-infra-iwan",
        "entityName": hostname,
    }
    return deviceData


def deleteDevice(token, serialNumber):
    url = f"https://172.23.1.10/api/v1/trust-point/serial-number/{serialNumber}"
    payload = {}
    headers = {"X-Auth-Token": f"{token}", "Content-Type": "application/json"}
    response = requests.request(
        "DELETE", url, headers=headers, data=payload, verify=False
    )
    if response.status_code == 202:
        print(f"The status code of delete device is: {response.status_code} \n")
    else:
        print("DEVICE COULD NOT BE DELETED")


def createDevice(token, payload):
    url = f"https://172.23.1.10/api/v1/trust-point"
    headers = {"X-Auth-Token": f"{token}", "Content-Type": "application/json"}
    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload), verify=False
    )
    print(f"The status code of create device is: {response.status_code} \n")


def getDeviceConfig(token, trustPointId):
    url = f"https://172.23.1.10/api/v1/trust-point/{trustPointId}/config"
    payload = {}
    headers = {"X-Auth-Token": f"{token}", "Content-Type": "application/json"}
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    data = response.json()["response"]["iosCli"][2]
    # data = response.json()
    finalConfigLine = data.replace("172.23.1.10", "173.252.189.173")
    print(finalConfigLine)


token = dnaAuth()
deleteDevice(token, serialNumber)
deviceData = getDeviceInfo(token, serialNumber)
pprint(deviceData)
createDevice(token, deviceData)
deviceId = getDeviceId(token, serialNumber)

message = (
    "## The following CLI commands have been generated to renew the certificate ##"
)
print("\n\n" + "#" * len(message))
print(message)
print("#" * len(message) + "\n\n")
getDeviceConfig(token, deviceId)
builTrustPoint(deviceData)
