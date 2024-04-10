import csv
from typing import Callable
from jinja2 import Template
from ipaddress import IPv4Network
from tqdm import tqdm

csvName = "dataForDeployScript.csv"
templateName = "redeploy-script.j2"
## How many addresses you want to exclude from dhcp scope, important to substract 1 from final number
DHCPEXCLUDE = 50

def generateTemplate(deviceData: dict[str, str], deviceName: str) -> None:
    redeploy_template = open(templateName, "r").read()
    template = Template(redeploy_template)
    deploymentScript = template.render(data=deviceData)
    with open(deviceName, "w+") as f:
        f.write(deploymentScript)


def getDataFromCsv(
    csvName: str, genTemplate: Callable[[dict[str, str], str], None]
) -> None:
    with open(csvName) as f:
        reader = csv.DictReader(f)
        for device in tqdm(reader, ascii=True):
            deviceData = device.copy()
            deviceName = device["routerName"]
            for vlan, network in device.items():
                if "vlan" in vlan and network:
                    subnet = IPv4Network(network)
                    networkAddress = subnet.network_address.__format__("s")
                    mask = subnet.netmask.__format__("s")
                    wildcard = subnet.hostmask.__format__("s")
                    gatewayIp = [ip for ip in subnet.hosts()][0].__format__("s")
                    dhcpExLastIp = [ip for ip in subnet.hosts()][
                        DHCPEXCLUDE
                    ].__format__("s")
                    deviceData[f"{vlan}Mask"] = mask
                    deviceData[f"{vlan}Wildcard"] = wildcard
                    deviceData[f"{vlan}DhcpExLastIp"] = dhcpExLastIp
                    deviceData[f"{vlan}gatewayIp"] = gatewayIp
                    deviceData[f"{vlan}networkAddress"] = networkAddress
            genTemplate(deviceData, deviceName)


if __name__ == "__main__":
    getDataFromCsv(csvName, generateTemplate)
