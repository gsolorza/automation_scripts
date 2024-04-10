#!/usr/bin/env python3
import requests
import json
from pprint import pprint
from connect import ssh
from ipaddress import IPv4Address, IPv4Network
import os
import sys

command = sys.argv[1]

os.environ['NET_TEXTFSM'] = '/Users/georgesolorzano/ansible/ansible_learning/inside-plastics/ntc-templates/templates'

wanIntNames = ['GigabitEthernet8', 
              'GigabitEthernet9', 
              'GigabitEthernet0/0/0', 
              'GigabitEthernet0/0/1', 
              'Dialer8']

def apicAuth():
    payload = json.dumps({
    "username": "",
    "password": ""
    })   
    headers = {
    'Content-Type': 'application/json'
    }
    url = "https://172.23.1.10/api/v1/ticket"
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    return response.json()["response"]["serviceTicket"]


def getApicInventory(token):
    url = "https://172.23.1.10/api/v1/network-device"
    payload={}
    headers = {
    'X-Auth-Token': f'{token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    return response.json()["response"]

def getApicDeviceIP(token, deviceId):
    deviceIPList = []
    url = f"https://172.23.1.10/api/v1/interface/network-device/{deviceId}"
    wanIntNames = ['GigabitEthernet8', 'GigabitEthernet9', 'GigabitEthernet0/0/0', 'GigabitEthernet0/0/1', 'Dialer8']
    payload={}
    headers = {
    'X-Auth-Token': f'{token}'
    }
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    deviceInterfaces = response.json()["response"]
    for interface in deviceInterfaces:
      if interface['portName'] in wanIntNames:
        if interface['ipv4Address'] != '0.0.0.0' and \
        interface['ipv4Address'] != None:
          ipAddress = IPv4Address(interface['ipv4Address'])
          deviceIPList.append(ipAddress)
    return deviceIPList
          

def getUmbrellaNetworks():
  orgId = "2485792"
  url = f"https://management.api.umbrella.com/v1/organizations/{orgId}/networks?limit=500"
  payload={}
  headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic MmJhMDEzZTI2OGVjNDI5MGExNzM0MzM0YTJlODM2ZDM6OWQzNWQ3YzQ3MWM5NDBjMTg3N2QxZGM4YjJjOGU5OTU='
  }
  response = requests.request("GET", url, headers=headers, data=payload)
  return response.json()

if command == 'network':
  token = apicAuth()
  apicDeviceList = getApicInventory(token)

  deviceInfo = []

  for device in apicDeviceList:
    deviceName = device['hostname'].rstrip('.NAP.local')                                                                                
    deviceId = device['id']
    deviceIpAddress = device['managementIpAddress']
    deviceIpList = getApicDeviceIP(token, deviceId)
    if not deviceIpList:
      '''
      In the case that pulling the IP from APIC-EM does not work because it is dhcp assigned
      The following code is to ssh into the device and pars the data to grab the IP
      '''
      data = ssh(deviceName, deviceIpAddress, 'lairdadmin', 'WgU0znN(qhxf')
      if data:
        for interface in data:
          intName = interface['intf']
          intIp = interface['ipaddr']
          if intName in wanIntNames:
            if intIp != 'unassigned':
              ipAddress = IPv4Address(intIp)
              deviceIpList.append(ipAddress)
        deviceInfo.append({'deviceName': deviceName, 'wanIp': deviceIpList, 'dynamicIP': 'YES'})
    elif deviceIpList:
      deviceInfo.append({'deviceName': deviceName, 'wanIp': deviceIpList, 'dynamicIP': 'NO'})

  match = []
  noMatch = []
  networkList = getUmbrellaNetworks()
  for device in deviceInfo:
    for devIpAddress in device['wanIp']:
      found = False
      for network in networkList:
        networkIp = network["ipAddress"]
        networkPrefix = '/'+str(network["prefixLength"])
        networkName = network["name"]
        network = IPv4Network(networkIp+networkPrefix)
        if devIpAddress in network:
            match.append({'deviceName': device['deviceName'], 'umbrellaNetworkName': networkName, 'wanIp': devIpAddress})
            found = True
            break
      if found == False:
        noMatch.append({'deviceName': device['deviceName'],'wanIp': devIpAddress, 'dynamicIP': device['dynamicIP']})

  pprint(noMatch)
  # pprint(match)

else:
  pass

