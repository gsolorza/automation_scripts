from napalm import get_network_driver
from pprint import pprint 

driver = get_network_driver("ios")

device = driver(hostname='10.253.8.89',
                username='cisco',
                password='cisco')

device.open()
device.is_alive()

pprint(device.get_interfaces())

